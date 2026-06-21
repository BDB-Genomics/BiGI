import os
import pytest
from bigi.parsers.generic import parse_generic_file
from bigi.parsers.snakemake import parse_snakemake_file

def test_generic_parser():
    """Test the regex-based generic AST parser using a dummy Python script."""
    # Create a temporary dummy python file
    dummy_code = '''
function my_function(a, b) {
    console.log("hello");
}

my_function(1, 2);
other_function();
    '''
    test_file = "/tmp/test_dummy.js"
    with open(test_file, "w") as f:
        f.write(dummy_code)
        
    try:
        res = parse_generic_file(test_file, "/tmp")
        defs, calls = res["definitions"], res["calls"]
        
        # Verify function definition
        assert len(defs) == 1
        assert defs[0]["name"] == "my_function"
        
        # Verify function calls
        call_names = [c["name"] for c in calls]
        assert "my_function" in call_names
        assert "other_function" in call_names
        assert "log" in call_names
    finally:
        os.remove(test_file)
