"""
eConverter web app: conversion results keep the zeros of their integer part.

The inline script in web-apps/econverter/index.html is run in Node with a
minimal DOM stub, and the result shown in the "toVal" field is checked.
Skipped when Node.js is not installed.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HTML = Path(__file__).parent.parent / "web-apps" / "econverter" / "index.html"
NODE = shutil.which("node")

HARNESS = r"""
const vm = require('vm');
const fs = require('fs');
const [htmlPath, casesJson] = process.argv.slice(1);  // node -e: argv[0] is node
const html = fs.readFileSync(htmlPath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

const els = {};
const listeners = {};
function el(id) {
  if (!els[id]) {
    els[id] = {
      id, value: '', textContent: '', innerHTML: '', selectedIndex: 0,
      addEventListener(type, fn) { (listeners[id] = listeners[id] || []).push(fn); },
    };
  }
  return els[id];
}
const tabs = ['length', 'weight', 'temp', 'area'].map(cat => ({
  dataset: { cat }, handlers: [],
  classList: { add() {}, remove() {} },
  addEventListener(type, fn) { this.handlers.push(fn); },
}));
const document = {
  getElementById: el,
  querySelectorAll: sel => (sel === '.conv-tab' ? tabs : []),
};
const ctx = vm.createContext({ document, navigator: {}, console });
vm.runInContext(script, ctx);

const out = [];
for (const [cat, value, from, to] of JSON.parse(casesJson)) {
  tabs.find(t => t.dataset.cat === cat).handlers.forEach(fn => fn());
  el('fromUnit').value = from;
  el('toUnit').value = to;
  el('fromVal').value = String(value);
  listeners.fromVal.forEach(fn => fn());
  out.push(el('toVal').value);
}
process.stdout.write(JSON.stringify(out));
"""

CASES = [
    # category, value, from, to, expected "toVal"
    ("length", 1, "km", "cm", "100000"),
    ("length", 1.2, "km", "cm", "120000"),
    ("weight", 500, "kg", "g", "500000"),
    ("area", 10, "ha", "m²", "100000"),
    ("length", 1, "km", "mm", "1e+6"),
    ("length", 1500, "km", "mm", "1.5e+9"),
    ("length", 1, "km", "m", "1000"),
    ("length", 100, "m", "cm", "10000"),
    ("length", 1, "mm", "m", "0.001"),
    ("length", 1, "in", "cm", "2.54"),
    ("length", 0, "km", "m", "0"),
    ("weight", 1, "mg", "t", "1e-9"),
    ("temp", 100, "°C", "°F", "212"),
    ("temp", -40, "°C", "°F", "-40"),
    ("temp", 0, "K", "°C", "-273.15"),
]


def run_cases(cases):
    proc = subprocess.run(
        [NODE, "-e", HARNESS, str(HTML), json.dumps([c[:4] for c in cases])],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_econverter_results():
    got = run_cases(CASES)
    failures = [
        f"{value} {frm} -> {to}: shows {shown!r}, expected {expected!r}"
        for (_, value, frm, to, expected), shown in zip(CASES, got)
        if shown != expected
    ]
    assert not failures, "\n".join(failures)


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_econverter_result_is_a_valid_number_input_value():
    # toVal is <input type="number">: no dangling "." and no "1.e+6".
    for shown in run_cases(CASES):
        assert re.fullmatch(r"-?\d+(\.\d*[1-9])?(e[+-]\d+)?", shown), shown
