#!/usr/bin/env python3
import json
import re
import sys
import xml.etree.ElementTree as ET


def status(value):
    text = str(value or "").lower()
    if text in {"fail", "failed", "error", "errored"}:
        return "failed"
    if text in {"skip", "skipped", "pending", "ignored", "notrun"}:
        return "skipped"
    return "passed"

def write(cases, target):
    suite = ET.Element("testsuite", {"name": "native-tests", "tests": str(len(cases)),
        "failures": str(sum(1 for c in cases if c[2] == "failed")),
        "skipped": str(sum(1 for c in cases if c[2] == "skipped"))})
    for classname, name, state, message in cases:
        case = ET.SubElement(suite, "testcase", {"classname": classname, "name": name})
        if state == "failed":
            node = ET.SubElement(case, "failure", {"message": message[:500]})
            node.text = message[:4000]
        elif state == "skipped":
            ET.SubElement(case, "skipped")
    ET.ElementTree(suite).write(target, encoding="utf-8", xml_declaration=True)

def go_json(path):
    cases = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        test = str(event.get("Test") or "")
        if not test or event.get("Action") not in {"pass", "fail", "skip"}:
            continue
        cases[(str(event.get("Package") or "go"), test)] = (
            str(event.get("Package") or "go"), test,
            status(event.get("Action")), str(event.get("Output") or "")[:1000])
    return list(cases.values())

def rust_text(path):
    cases = []
    for line in open(path, encoding="utf-8", errors="replace"):
        match = re.match(r"^\s*test\s+(\S+)\s+\.\.\.\s+(ok|FAILED|ignored)\s*$", line)
        if match:
            full = match.group(1)
            classname, _, name = full.rpartition("::")
            cases.append((classname or "rust", name or full,
                          status("skip" if match.group(2) == "ignored" else match.group(2)), ""))
    return cases

def rspec_json(path):
    payload = json.load(open(path, encoding="utf-8", errors="replace"))
    cases = []
    for item in payload.get("examples") or []:
        name = str(item.get("full_description") or item.get("description") or "")
        if name:
            cases.append((str(item.get("file_path") or "rspec").lstrip("./"), name,
                          status(item.get("status")), ""))
    return cases

def trx(path):
    root = ET.parse(path).getroot()
    ns = root.tag.split("}", 1)[0] + "}" if root.tag.startswith("{") else ""
    names = {}
    for unit in root.findall(f".//{ns}UnitTest"):
        method = unit.find(f"{ns}TestMethod")
        if method is not None and unit.get("id"):
            names[unit.get("id")] = f"{method.get('className') or 'dotnet'}::{method.get('name') or ''}"
    cases = []
    for result in root.findall(f".//{ns}UnitTestResult"):
        full = names.get(result.get("testId") or "") or result.get("testName") or ""
        if full:
            classname, _, name = full.rpartition("::")
            cases.append((classname or "dotnet", name or full, status(result.get("outcome")), ""))
    return cases

def main():
    mode, source, target = sys.argv[1], sys.argv[2], sys.argv[3]
    cases = {"go-json": go_json, "rust-text": rust_text,
             "rspec-json": rspec_json, "trx": trx}[mode](source)
    write(cases, target)

if __name__ == "__main__":
    main()
