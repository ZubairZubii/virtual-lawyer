"use client"

/**
 * Backend case_predictor returns sentence_prediction as { predictions: [...], overall_risk }
 * and timeline_prediction as { investigation, trial_duration, ... } — not plain strings.
 */

export function SentencePredictionDisplay({ value }: { value: unknown }) {
  if (value == null || value === false) return null
  if (typeof value === "string") {
    return <p className="font-medium">{value}</p>
  }
  if (typeof value === "object" && value !== null && "predictions" in value) {
    const v = value as {
      predictions: Array<Record<string, unknown>>
      overall_risk?: number
    }
    return (
      <div className="space-y-3">
        {v.overall_risk != null && (
          <p className="text-sm text-muted-foreground">
            Risk context:{" "}
            <span className="font-medium text-foreground">{v.overall_risk}%</span>
          </p>
        )}
        <ul className="space-y-2">
          {Array.isArray(v.predictions) &&
            v.predictions.map((row, i) => (
              <li
                key={i}
                className="rounded-md border border-border/50 bg-muted/30 p-3 text-sm"
              >
                <p className="font-medium">Section {String(row.section ?? "")}</p>
                <p className="text-foreground">{String(row.likely_sentence ?? "")}</p>
                {row.probability != null && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    Probability: {Math.round(Number(row.probability) * 100)}% · Range:{" "}
                    {String(row.min_sentence ?? "")} – {String(row.max_sentence ?? "")}
                  </p>
                )}
              </li>
            ))}
        </ul>
      </div>
    )
  }
  return (
    <pre className="max-h-48 overflow-auto rounded-md bg-muted/50 p-3 text-xs">
      {JSON.stringify(value, null, 2)}
    </pre>
  )
}

export function TimelinePredictionDisplay({ value }: { value: unknown }) {
  if (value == null || value === false) return null
  if (typeof value === "string") {
    return <p className="font-medium">{value}</p>
  }
  if (typeof value === "object" && value !== null) {
    const entries = Object.entries(value as Record<string, unknown>)
    return (
      <dl className="grid gap-2 text-sm">
        {entries.map(([k, val]) => (
          <div
            key={k}
            className="flex flex-col gap-0.5 border-b border-border/30 pb-2 last:border-0 sm:flex-row sm:justify-between sm:gap-4"
          >
            <dt className="text-muted-foreground capitalize">
              {k.replace(/_/g, " ")}
            </dt>
            <dd className="font-medium sm:text-right">{String(val)}</dd>
          </div>
        ))}
      </dl>
    )
  }
  return <p className="text-sm text-muted-foreground">{String(value)}</p>
}
