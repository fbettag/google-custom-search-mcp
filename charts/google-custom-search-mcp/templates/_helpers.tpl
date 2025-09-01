{{/*
Expand the name of the chart.
*/}}
{{- define "google-custom-search-mcp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "google-custom-search-mcp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "google-custom-search-mcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "google-custom-search-mcp.labels" -}}
helm.sh/chart: {{ include "google-custom-search-mcp.chart" . }}
{{ include "google-custom-search-mcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "google-custom-search-mcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "google-custom-search-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "google-custom-search-mcp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "google-custom-search-mcp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create environment variables for Google configuration
*/}}
{{- define "google-custom-search-mcp.envVars" -}}
- name: GOOGLE_SEARCH_ENGINE_ID
  value: {{ .Values.google.searchEngineId | quote }}
{{- if .Values.serviceAccount.base64.enabled }}
- name: GOOGLE_SERVICE_ACCOUNT_BASE64
  value: {{ .Values.serviceAccount.base64.value | quote }}
{{- end }}
{{- if .Values.env.debug }}
- name: DEBUG
  value: "1"
{{- end }}
{{- range $key, $value := .Values.env.extra }}
- name: {{ $key | upper }}
  value: {{ $value | quote }}
{{- end }}
{{- end }}