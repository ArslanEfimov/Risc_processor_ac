import contextlib
import io
import logging
import os
import shutil
import tempfile

import machine
import pytest
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_asm_and_machine(golden, caplog, temp_dir):
    """Почти полная копия test_translator_and_machine из golden_bf_test. Детали
    см. там."""
    caplog.set_level(logging.DEBUG)

    source = os.path.join(temp_dir, "source.asm")
    input_stream = os.path.join(temp_dir, "input.txt")
    target = os.path.join(temp_dir, "target.o")

    with open(source, "w", encoding="utf-8") as file:
        file.write(golden["in_source"])
    with open(input_stream, "w", encoding="utf-8") as file:
        file.write(golden["in_stdin"])

    with contextlib.redirect_stdout(io.StringIO()) as stdout:
        translator.main(source, target)
        print("============================================================")
        machine.main(target, input_stream)

    with open(target, encoding="utf-8") as file:
        code = file.read()

    assert code == golden.out["out_code"]
    assert stdout.getvalue() == golden.out["out_stdout"]
    assert caplog.text == golden.out["out_log"]


@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)
