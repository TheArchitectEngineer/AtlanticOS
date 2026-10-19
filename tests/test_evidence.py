import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('evidence_validator', ROOT/'tools/evidence-validator/validate_evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'log.txt').write_bytes(b'host fixture')
        self.record = {'schema_version':1,'label':'HOST_TESTED','scope':'fixture',
                       'artifacts':[{'path':'log.txt','sha256':hashlib.sha256(b'host fixture').hexdigest()}]}

    def check(self):
        path = self.root/'manifest.json'
        path.write_text(json.dumps(self.record))
        return evidence.validate(path)

    def test_valid_host_record(self):
        self.assertEqual(self.check(),1)

    def test_hash_mismatch(self):
        (self.root/'log.txt').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.check()

    def test_no_upgrade_to_device_without_physical_artifacts(self):
        self.record['label'] = 'DEVICE_VERIFIED'
        with self.assertRaises(ValueError):
            self.check()

    def test_path_traversal_and_duplicates(self):
        self.record['artifacts'][0]['path'] = '../outside.txt'
        with self.assertRaises(ValueError):
            self.check()
        self.record['artifacts'][0]['path'] = 'log.txt'
        self.record['artifacts'].append(self.record['artifacts'][0].copy())
        with self.assertRaises(ValueError):
            self.check()

    def test_device_metadata_does_not_replace_binary_and_capture(self):
        self.record.update(label='DEVICE_VERIFIED',board_id='fixture',firmware_id='fixture',
                           binary_sha256='0'*64,physical_capture_sha256='1'*64,
                           android_recovery_result='fixture',timestamp='fixture')
        with self.assertRaises(ValueError):
            self.check()
