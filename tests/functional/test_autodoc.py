# -*- coding: utf-8 -*-
"""Test dbtoyaml and yamltodb using autodoc schema

See http://cvs.pgfoundry.org/cgi-bin/cvsweb.cgi/~checkout~/autodoc/autodoc/
regressdatabase.sql?rev=1.2
"""
import unittest

from pyrseas.testutils import DbMigrateTestCase


class AutodocTestCase(DbMigrateTestCase):

    @classmethod
    def tearDownClass(cls):
        cls.remove_tempfiles('autodoc')
        cls.remove_tempfiles('empty')

    def test_autodoc(self):
        # Create the source schema
        self.execute_script(__file__, 'autodoc-schema.sql')

        # Run pg_dump against source database
        srcdump = self.tempfile_path('autodoc-src.dump')
        self.run_pg_dump(srcdump, True)

        # Create source YAML file
        srcyaml = self.tempfile_path('autodoc-src.yaml')
        self.create_yaml(srcyaml, True)

        # Run pg_dump/dbtoyaml against empty target database
        emptydump = self.tempfile_path('empty.dump')
        self.run_pg_dump(emptydump)
        emptyyaml = self.tempfile_path('empty.yaml')
        self.create_yaml(emptyyaml)

        # Migrate the target database
        targsql = self.tempfile_path('autodoc.sql')
        self.migrate_target(srcyaml, targsql)

        # Run pg_dump against target database
        targdump = self.tempfile_path('autodoc.dump')
        self.run_pg_dump(targdump)

        # Create target YAML file
        targyaml = self.tempfile_path('autodoc.yaml')
        self.create_yaml(targyaml)

        # diff autodoc-src.dump against autodoc.dump
        self.assertEqual(open(srcdump).readlines(), open(targdump).readlines())
        # diff autodoc-src.yaml against autodoc.yaml
        self.assertEqual(open(srcyaml).readlines(), open(targyaml).readlines())

        # Undo the changes
        self.migrate_target(emptyyaml, targsql)

        # Run pg_dump against target database
        self.run_pg_dump(targdump)

        # Create target YAML file
        self.create_yaml(targyaml)

        # diff empty.dump against autodoc.dump
        self.assertEqual(open(emptydump).readlines(),
                         open(targdump).readlines())
        # diff empty.yaml against autodoc.yaml
        self.assertEqual(open(emptyyaml).readlines(),
                         open(targyaml).readlines())


def suite():
    tests = unittest.TestLoader().loadTestsFromTestCase(AutodocTestCase)
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
