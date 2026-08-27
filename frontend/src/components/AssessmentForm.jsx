import { useState } from "react";

const NUMERIC_FIELDS = [
  { name: "age", label: "Age", unit: "years", min: 1, max: 120, step: 1 },
  { name: "bmi", label: "BMI", unit: "kg/m²", min: 10, max: 70, step: 0.1 },
  { name: "systolic_bp", label: "Systolic BP", unit: "mmHg", min: 60, max: 260, step: 1 },
  { name: "diastolic_bp", label: "Diastolic BP", unit: "mmHg", min: 30, max: 160, step: 1 },
  { name: "cholesterol", label: "Cholesterol", unit: "mg/dL", min: 50, max: 500, step: 1 },
  { name: "hdl", label: "HDL", unit: "mg/dL", min: 10, max: 150, step: 1 },
  { name: "ldl", label: "LDL", unit: "mg/dL", min: 10, max: 350, step: 1 },
  { name: "glucose", label: "Glucose", unit: "mg/dL", min: 30, max: 600, step: 1 },
  { name: "creatinine", label: "Creatinine", unit: "mg/dL", min: 0.1, max: 15, step: 0.01 },
  { name: "hemoglobin", label: "Hemoglobin", unit: "g/dL", min: 3, max: 22, step: 0.1 },
  { name: "wbc", label: "WBC", unit: "×10⁹/L", min: 0.5, max: 40, step: 0.1 },
  { name: "length_of_stay", label: "Length of stay", unit: "days", min: 0, max: 120, step: 1 },
];

const CATEGORY_FIELDS = ["sex", "smoking_status", "alcohol_use", "primary_diagnosis", "medications"];

const FIELD_LABELS = {
  sex: "Sex",
  smoking_status: "Smoking status",
  alcohol_use: "Alcohol use",
  primary_diagnosis: "Primary diagnosis",
  medications: "Medications",
};

const DEFAULTS = {
  age: 65, bmi: 27, systolic_bp: 130, diastolic_bp: 82, cholesterol: 190,
  hdl: 48, ldl: 115, glucose: 140, creatinine: 1.0, hemoglobin: 13,
  wbc: 7.2, length_of_stay: 4, hypertension: false,
};

function Section({ title, children }) {
  return (
    <div className="mb-8">
      <h3 className="font-display text-sm tracking-wide uppercase text-[var(--ink-soft)] mb-4 pb-2 border-b border-[var(--border)]">
        {title}
      </h3>
      <div className="grid grid-cols-2 gap-x-6 gap-y-5">{children}</div>
    </div>
  );
}

function NumberInput({ field, value, onChange }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-[var(--ink)]">{field.label}</span>
      <span className="text-xs text-[var(--ink-soft)] ml-1">({field.unit})</span>
      <input
        type="number"
        required
        min={field.min}
        max={field.max}
        step={field.step}
        value={value}
        onChange={(e) => onChange(field.name, e.target.value)}
        className="mt-1 w-full rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm
                   font-mono focus:outline-none focus:ring-2 focus:ring-[var(--teal)] focus:border-transparent"
      />
    </label>
  );
}

function SelectInput({ name, options, value, onChange }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-[var(--ink)]">{FIELD_LABELS[name]}</span>
      <select
        required
        value={value ?? ""}
        onChange={(e) => onChange(name, e.target.value)}
        className="mt-1 w-full rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-[var(--teal)] focus:border-transparent"
      >
        <option value="" disabled>Select...</option>
        {(options || []).map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </label>
  );
}

function TextInput({ name, label, placeholder, value, onChange, helpText }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-[var(--ink)]">{label}</span>
      <input
        type="text"
        placeholder={placeholder}
        value={value ?? ""}
        onChange={(e) => onChange(name, e.target.value)}
        className="mt-1 w-full rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-[var(--teal)] focus:border-transparent"
      />
      {helpText && <span className="block text-xs text-[var(--ink-soft)] mt-1">{helpText}</span>}
    </label>
  );
}

export default function AssessmentForm({ formOptions, onSubmit, submitting }) {
  const [values, setValues] = useState({ ...DEFAULTS });

  const update = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...values,
      patient_reference: values.patient_reference?.trim() ? values.patient_reference.trim() : null,
      age: Number(values.age),
      bmi: Number(values.bmi),
      systolic_bp: Number(values.systolic_bp),
      diastolic_bp: Number(values.diastolic_bp),
      cholesterol: Number(values.cholesterol),
      hdl: Number(values.hdl),
      ldl: Number(values.ldl),
      glucose: Number(values.glucose),
      creatinine: Number(values.creatinine),
      hemoglobin: Number(values.hemoglobin),
      wbc: Number(values.wbc),
      length_of_stay: Number(values.length_of_stay),
      hypertension: Boolean(values.hypertension),
    };
    onSubmit(payload);
  };

  const missingCategory = CATEGORY_FIELDS.some((f) => !values[f]);

  return (
    <form onSubmit={handleSubmit} className="bg-[var(--panel)] rounded-lg border border-[var(--border)] p-8">
      <div className="mb-8">
        <TextInput
          name="patient_reference"
          label="Patient reference"
          placeholder="e.g. hospital MRN"
          value={values.patient_reference}
          onChange={update}
          helpText="Optional. Enables viewing this patient's assessment history. Leave blank for a one-off assessment."
        />
      </div>

      <Section title="Demographics">
        <NumberInput field={NUMERIC_FIELDS[0]} value={values.age} onChange={update} />
        <SelectInput name="sex" options={formOptions?.sex} value={values.sex} onChange={update} />
      </Section>

      <Section title="Vitals & Labs">
        {NUMERIC_FIELDS.slice(1, 11).map((f) => (
          <NumberInput key={f.name} field={f} value={values[f.name] ?? ""} onChange={update} />
        ))}
      </Section>

      <Section title="Lifestyle & History">
        <SelectInput name="smoking_status" options={formOptions?.smoking_status} value={values.smoking_status} onChange={update} />
        <SelectInput name="alcohol_use" options={formOptions?.alcohol_use} value={values.alcohol_use} onChange={update} />
        <SelectInput name="primary_diagnosis" options={formOptions?.primary_diagnosis} value={values.primary_diagnosis} onChange={update} />
        <SelectInput name="medications" options={formOptions?.medications} value={values.medications} onChange={update} />
        <label className="flex items-center gap-2 mt-1">
          <input
            type="checkbox"
            checked={values.hypertension}
            onChange={(e) => update("hypertension", e.target.checked)}
            className="h-4 w-4 rounded border-[var(--border)] accent-[var(--teal)]"
          />
          <span className="text-sm font-medium">Hypertension</span>
        </label>
      </Section>

      <Section title="Discharge">
        <NumberInput field={NUMERIC_FIELDS[11]} value={values.length_of_stay ?? ""} onChange={update} />
      </Section>

      <button
        type="submit"
        disabled={submitting || missingCategory}
        className="w-full rounded-md bg-[var(--teal)] text-white font-medium py-3
                   hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
      >
        {submitting ? "Assessing..." : "Assess readmission risk"}
      </button>
    </form>
  );
}
