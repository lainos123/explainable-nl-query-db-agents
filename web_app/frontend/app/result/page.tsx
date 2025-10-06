"use client"

import React, { useEffect, useState } from 'react';

function toCSV(headers: string[], rows: Array<Record<string, any>>) {
  const esc = (v: any) => '"' + String(v ?? '').replace(/"/g, '""') + '"';
  return [headers.join(','), ...rows.map(r => headers.map(h => esc(r[h])).join(','))].join('\r\n');
}

const ResultPage: React.FC = () => {
  const [rows, setRows] = useState<Array<Record<string, any>> | null>(null);
  const [headers, setHeaders] = useState<string[]>([]);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem('last_full_result');
      if (!raw) {
        setRows(null);
        return;
      }
      const parsed = JSON.parse(raw);
      // Normalize: if parsed is object with key `result`, use that; else if array, use it
      let data: any = parsed;
      if (parsed && typeof parsed === 'object' && parsed.result) data = parsed.result;
      if (Array.isArray(data)) {
        setRows(data as Array<Record<string, any>>);
        const hdrs = Array.from(data.reduce((acc: Set<string>, r: any) => { Object.keys(r || {}).forEach(k => acc.add(k)); return acc; }, new Set<string>()));
        setHeaders(hdrs);
      } else if (data && typeof data === 'object') {
        // single object -> show as single-row
        setRows([data]);
        setHeaders(Object.keys(data));
      } else {
        setRows(null);
      }
    } catch (e) {
      setRows(null);
    }
  }, []);

  const handleDownload = () => {
    if (!rows || headers.length === 0) return;
    const csv = toCSV(headers, rows);
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `result_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  };

return (
  // Full screen overlay dark-themed
  <div className="fixed inset-0 z-50 bg-gray-900 text-gray-100 p-4 overflow-auto">
    <div className="max-w-[98vw] mx-auto">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <button
            className="inline-flex items-center gap-2 px-3 py-1 rounded bg-gray-800 text-white text-sm"
            onClick={() => {
              try { sessionStorage.removeItem('last_full_result'); } catch {}
              window.history.back();
            }}
          >
            ← Back
          </button>
          <h1 className="text-lg font-semibold ml-2">Full Result</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            className={`px-3 py-1 rounded text-sm ${
              rows ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-gray-700 text-gray-300 cursor-not-allowed'
            }`}
            onClick={handleDownload}
            disabled={!rows}
          >
            Download CSV
          </button>
        </div>
      </div>

      {rows && rows.length > 0 ? (
        <div className="w-full bg-gray-900">
          <div className="overflow-auto border border-gray-700 rounded bg-gray-900">
            <table className="min-w-full text-sm table-auto">
              <thead className="sticky top-0 bg-gray-800">
                <tr>
                  {headers.map(h => (
                    <th
                      key={h}
                      className="px-3 py-2 text-left text-xs uppercase tracking-wide text-gray-300 border-b border-gray-700"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-gray-900' : 'bg-gray-800'}>
                    {headers.map(h => (
                      <td
                        key={h}
                        className="px-2 py-1 align-top border-b border-gray-700"
                      >
                        {String((r as any)[h] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-gray-400">
          No full result available. Trigger a query with "View all columns & rows" to populate.
        </div>
      )}
    </div>
  </div>
);
};

export default ResultPage;
