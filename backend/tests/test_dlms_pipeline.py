import os
import asyncio
import pytest

from app.plugins.base import ToolInput
from app.plugins.yara import YaraPlugin
from app.plugins.strings import StringsPlugin
from app.plugins.security_suite import SecuritySuitePlugin
from analyzer.modules.report_generator import determine_protocol_verdict

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
V1_PATH = os.path.join(FIXTURES_DIR, "synthetic_dlms_variant1.bin")
V2_PATH = os.path.join(FIXTURES_DIR, "synthetic_dlms_variant2.bin")

@pytest.fixture(scope="module", autouse=True)
def setup_fixtures():
    # Make sure fixtures exist
    assert os.path.exists(V1_PATH), f"Missing {V1_PATH}"
    assert os.path.exists(V2_PATH), f"Missing {V2_PATH}"

def test_dlms_variant1_security_suite_2():
    tool_input = ToolInput(target_filepath=V1_PATH)
    
    # 1. String Scanner
    strings_plugin = StringsPlugin()
    strings_out = asyncio.run(strings_plugin.execute_real(tool_input))
    assert strings_out.success is True
    string_matches = strings_out.parsed_metrics.get("matches", {})

    # 2. YARA Scanner
    yara_plugin = YaraPlugin()
    yara_out = asyncio.run(yara_plugin.execute_real(tool_input))
    assert yara_out.success is True
    yara_matches = yara_out.parsed_metrics.get("matches", [])
    
    # Check that YARA found our crypto library and OBIS codes
    rule_names = [m["rule"] for m in yara_matches]
    assert "mbedTLS_Library_Identification" in rule_names, f"YARA failed to detect mbedTLS in {rule_names}"
    assert "DLMS_COSEM_OBIS_Code_Known" in rule_names, "YARA failed to identify known OBIS codes"
    
    # Check OBIS resolution meaning
    obis_match = next(m for m in yara_matches if m["rule"] == "DLMS_COSEM_OBIS_Code_Known")
    assert "Active energy import (+A)" in obis_match["description"] or "Meter serial number" in obis_match["description"]

    # 3. Protocol Verdict
    verdict = determine_protocol_verdict(string_matches, yara_matches)
    assert verdict == "DLMS/COSEM confirmed"

    # 4. Security Suite Verification
    sec_plugin = SecuritySuitePlugin()
    sec_out = asyncio.run(sec_plugin.execute_real(tool_input))
    assert sec_out.success is True
    
    suite = sec_out.parsed_metrics.get("suite")
    has_aes = sec_out.parsed_metrics.get("has_aes")
    has_ecdsa = sec_out.parsed_metrics.get("has_ecdsa")
    
    assert suite == 2, f"Expected Suite 2, got Suite {suite}"
    assert has_aes is True
    assert has_ecdsa is True


def test_dlms_variant2_security_suite_0():
    tool_input = ToolInput(target_filepath=V2_PATH)
    
    strings_plugin = StringsPlugin()
    strings_out = asyncio.run(strings_plugin.execute_real(tool_input))
    string_matches = strings_out.parsed_metrics.get("matches", {})

    yara_plugin = YaraPlugin()
    yara_out = asyncio.run(yara_plugin.execute_real(tool_input))
    yara_matches = yara_out.parsed_metrics.get("matches", [])

    rule_names = [m["rule"] for m in yara_matches]
    assert "DLMS_COSEM_OBIS_Code_Known" in rule_names
    
    verdict = determine_protocol_verdict(string_matches, yara_matches)
    assert verdict == "DLMS/COSEM confirmed"

    sec_plugin = SecuritySuitePlugin()
    sec_out = asyncio.run(sec_plugin.execute_real(tool_input))
    
    suite = sec_out.parsed_metrics.get("suite")
    has_aes = sec_out.parsed_metrics.get("has_aes")
    has_ecdsa = sec_out.parsed_metrics.get("has_ecdsa")
    
    assert suite == 0, f"Expected Suite 0, got Suite {suite}"
    assert has_aes is False
    assert has_ecdsa is False
