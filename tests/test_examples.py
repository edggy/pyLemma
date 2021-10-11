# coding=utf-8
from pathlib import Path

import parsers

ROOT_DIR = Path("..").absolute()


def validate_file(file: Path):
    proofs = parsers.defaultProofParser(str(file))

    return all(proof.verify() for proof in proofs.values())


def test_f_lemmas():
    rules_dir = ROOT_DIR / "Examples/F Lemmas"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_fo_logic():
    rules_dir = ROOT_DIR / "Examples/FO Logic"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_math():
    rules_dir = ROOT_DIR / "Examples/Math"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_ks_logic():
    rules_dir = ROOT_DIR / "Examples/KS Logic"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_natural_logic():
    rules_dir = ROOT_DIR / "Examples/Natural Logic"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_set():
    rules_dir = ROOT_DIR / "Examples/Set"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_tf_algebra():
    rules_dir = ROOT_DIR / "Examples/TF Algebra"
    for file in rules_dir.iterdir():
        assert validate_file(file)


def test_tf_logic():
    rules_dir = ROOT_DIR / "Examples/TF Logic"
    for file in rules_dir.iterdir():
        assert validate_file(file)
