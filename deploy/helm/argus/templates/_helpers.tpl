{{- define "argus.labels" -}}
app.kubernetes.io/part-of: argus
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}
