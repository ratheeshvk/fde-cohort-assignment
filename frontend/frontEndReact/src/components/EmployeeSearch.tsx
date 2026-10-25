import { useState } from 'react';
import type { Employee } from '../type';

interface EmployeeSearchProps {
  employees: Employee[];
  selectedId: number | null;
  onChange: (employeeId: number | null) => void;
}

export default function EmployeeSearch({ employees, selectedId, onChange }: EmployeeSearchProps) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);

  const selected = employees.find((e) => e.id === selectedId) ?? null;
  const term = query.trim().toLowerCase();
  const matches = term
    ? employees.filter(
        (e) => e.name.toLowerCase().includes(term) || e.employee_id.toLowerCase().includes(term),
      )
    : employees;

  const choose = (employeeId: number | null) => {
    onChange(employeeId);
    setQuery('');
    setOpen(false);
  };

  return (
    <div className="employee-search">
      <input
        type="text"
        placeholder={selected ? `${selected.name} (${selected.employee_id})` : 'All Employees'}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
      />
      {open && (
        <ul className="employee-options">
          {/* onMouseDown + preventDefault so the pick happens before the input blurs */}
          <li
            className={selectedId === null ? 'active' : ''}
            onMouseDown={(e) => {
              e.preventDefault();
              choose(null);
            }}
          >
            All Employees
          </li>
          {matches.map((emp) => (
            <li
              key={emp.id}
              className={emp.id === selectedId ? 'active' : ''}
              onMouseDown={(e) => {
                e.preventDefault();
                choose(emp.id);
              }}
            >
              {emp.name} <span className="muted">({emp.employee_id})</span>
            </li>
          ))}
          {matches.length === 0 && <li className="muted">No matching employees</li>}
        </ul>
      )}
    </div>
  );
}
