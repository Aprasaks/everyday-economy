import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from publisher import KST, database, fingerprint, render, run_job, upcoming, validate_article


def article():
    return {'title': 'Why lower inflation does not mean lower prices',
            'question': 'Why do prices stay high when inflation falls?',
            'summary': 'Lower inflation means prices rise more slowly, not necessarily that prices fall.',
            'sections': [{'heading': f'Explanation {i}', 'paragraphs': [' '.join(['example'] * 180)]}
                         for i in range(3)],
            'sources': [{'title': 'BLS', 'url': 'https://www.bls.gov/cpi/', 'date_context': 'Illustrative test source'},
                        {'title': 'Fed', 'url': 'https://www.federalreserve.gov/', 'date_context': 'Illustrative test source'}],
            'image_prompt': 'Abstract grocery basket and receipt', 'image_alt': 'Illustrated grocery basket'}


class FakeServices:
    def __init__(self, approve=True, insert_error=False):
        self.approve = approve
        self.insert_error = insert_error
        self.writes = []
        self.images = 0

    def posts(self):
        return []

    def ask(self, prompt):
        if prompt.startswith('Research and write'):
            return article(), {'test': True}
        return {'approved': self.approve, 'issues': [] if self.approve else ['Unsupported claim'],
                'verified_sources': [s['url'] for s in article()['sources']]}, {'test': True}

    def image(self, *args):
        self.images += 1
        return 'https://assets.example.org/image.png'

    def blogger(self, method, path, **kwargs):
        self.writes.append((method, path))
        if self.insert_error:
            raise TimeoutError('Ambiguous create')
        if path == '/posts':
            self.content = kwargs['json']['content']
            return {'id': '123'}
        if method == 'POST':
            self.slot = kwargs['params']['publishDate']
            return {'id': '123'}
        return {'id': '123', 'status': 'SCHEDULED', 'content': self.content, 'published': self.slot}


class PublisherTests(unittest.TestCase):
    def test_slot_boundaries(self):
        for hour in (9, 12, 18):
            target = datetime(2026, 11, 4, hour, tzinfo=KST)
            for minutes in (10, 30, 60):
                self.assertEqual(upcoming(target - timedelta(minutes=minutes)), target)
            self.assertIsNone(upcoming(target - timedelta(minutes=9)))
            self.assertIsNone(upcoming(target + timedelta(minutes=1)))

    def test_html_injection_escaped(self):
        a = article()
        a['sections'][0]['paragraphs'] = ['<script>alert(1)</script>']
        self.assertNotIn('<script>', render(a, 'https://assets.example.org/x.png', 'test'))

    def test_primary_evidence_required(self):
        a = article()
        a['sources'] = [{'url': 'https://news.example.org/x'}, {'url': 'https://news.example.org/y'}]
        with self.assertRaises(ValueError):
            validate_article(a)

    def test_oversize_summary_blocked(self):
        a = article()
        a['summary'] = 'x' * 151
        with self.assertRaises(ValueError):
            validate_article(a)

    def test_rejected_review_cannot_generate_or_publish(self):
        with tempfile.TemporaryDirectory() as root:
            db = database(str(Path(root) / 'state.sqlite3'))
            services = FakeServices(approve=False)
            target = datetime.now(KST) + timedelta(minutes=30)
            with self.assertRaises(RuntimeError):
                run_job(db, target, services, root, publish=True)
            self.assertEqual(services.images, 0)
            self.assertEqual(services.writes, [])
            self.assertEqual(db.execute('SELECT state FROM jobs').fetchone()['state'], 'BLOCKED')

    def test_slot_once_and_draft_only_mode(self):
        with tempfile.TemporaryDirectory() as root:
            db = database(str(Path(root) / 'state.sqlite3'))
            target = datetime.now(KST) + timedelta(minutes=30)
            services = FakeServices()
            self.assertEqual(run_job(db, target, services, root), 'ready-not-published')
            self.assertEqual(run_job(db, target, services, root), 'already-recorded')
            self.assertEqual(services.writes, [])

    def test_schedule_timestamp_and_saved_post_id(self):
        with tempfile.TemporaryDirectory() as root:
            db = database(str(Path(root) / 'state.sqlite3'))
            target = datetime.now(KST) + timedelta(minutes=30)
            services = FakeServices()
            self.assertEqual(run_job(db, target, services, root, publish=True), 'scheduled')
            row = db.execute('SELECT * FROM jobs').fetchone()
            self.assertEqual(row['post_id'], '123')
            self.assertEqual(row['state'], 'SCHEDULED')
            self.assertEqual(services.slot, target.isoformat())

    def test_uncertain_create_never_repeated(self):
        with tempfile.TemporaryDirectory() as root:
            db = database(str(Path(root) / 'state.sqlite3'))
            target = datetime.now(KST) + timedelta(minutes=30)
            services = FakeServices(insert_error=True)
            with self.assertRaises(RuntimeError):
                run_job(db, target, services, root, publish=True)
            self.assertEqual(db.execute('SELECT state FROM jobs').fetchone()['state'], 'NEEDS_RECONCILIATION')
            self.assertEqual(run_job(db, target, services, root, publish=True), 'already-recorded')
            self.assertEqual(len(services.writes), 1)


if __name__ == '__main__':
    unittest.main()
