import { useEffect, useState } from 'react';

interface MermaidChartProps {
  chart: string;
}

export default function MermaidChart({ chart }: MermaidChartProps) {
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setSvg(null);
    setError(false);

    (async () => {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: 'dark',
          securityLevel: 'loose',
          flowchart: { curve: 'basis' },
        });

        const id = `m-${Math.random().toString(36).slice(2, 9)}`;
        const { svg: result } = await mermaid.render(id, chart);

        if (!cancelled) {
          setSvg(result);
        }
      } catch {
        if (!cancelled) {
          setError(true);
        }
      }
    })();

    return () => { cancelled = true; };
  }, [chart]);

  if (error) {
    return (
      <div className="w-full overflow-x-auto p-4 bg-gray-900/50 rounded-2xl border border-gray-800 min-h-[200px]">
        <pre className="text-red-400 text-xs p-4 whitespace-pre-wrap">{chart}</pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="w-full flex items-center justify-center p-4 bg-gray-900/50 rounded-2xl border border-gray-800 min-h-[200px]">
        <div className="text-gray-500 text-sm animate-pulse">Rendering diagram...</div>
      </div>
    );
  }

  return (
    <div
      className="w-full flex justify-center overflow-x-auto p-4 bg-gray-900/50 rounded-2xl border border-gray-800"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
