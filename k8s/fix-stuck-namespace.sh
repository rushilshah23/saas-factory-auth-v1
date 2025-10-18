#!/bin/bash

echo "🔍 Checking for namespaces stuck in Terminating state..."
stuck_namespaces=$(kubectl get ns --no-headers | awk '$2=="Terminating"{print $1}')

if [ -z "$stuck_namespaces" ]; then
  echo "✅ No namespaces are stuck in Terminating state."
  exit 0
fi

echo "⚠️ Found terminating namespaces:"
echo "$stuck_namespaces"
echo

for ns in $stuck_namespaces; do
  echo "🧽 Cleaning up namespace: $ns ..."

  # Backup JSON before modifying
  kubectl get ns "$ns" -o json > "/tmp/${ns}-ns.json"

  # Remove finalizers from namespace JSON
  cat "/tmp/${ns}-ns.json" | jq 'del(.spec.finalizers)' > "/tmp/${ns}-patched.json"

  # Force finalize deletion
  kubectl replace --raw "/api/v1/namespaces/${ns}/finalize" -f "/tmp/${ns}-patched.json" >/dev/null 2>&1

  # Verify
  sleep 1
  if kubectl get ns "$ns" >/dev/null 2>&1; then
    echo "❌ Namespace $ns still exists. Manual cleanup may be needed."
  else
    echo "✅ Namespace $ns successfully removed."
  fi

  echo
done

echo "🎉 Cleanup complete!"
