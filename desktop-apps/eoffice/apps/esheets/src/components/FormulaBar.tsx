interface FormulaBarProps {
  cellAddress: string;
  formulaValue: string;
  onFormulaChange: (value: string) => void;
  onFormulaSubmit: () => void;
}

export default function FormulaBar({
  cellAddress,
  formulaValue,
  onFormulaChange,
  onFormulaSubmit,
}: FormulaBarProps) {
  return (
    <div className="formula-bar">
      <input
        className="formula-bar-address"
        value={cellAddress}
        readOnly
      />
      <div className="formula-bar-fx">fx</div>
      <input
        className="formula-bar-input"
        value={formulaValue}
        onChange={(e) => onFormulaChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            onFormulaSubmit();
          }
        }}
        placeholder="Enter value or formula (e.g. =SUM(A1:A5))"
      />
    </div>
  );
}
