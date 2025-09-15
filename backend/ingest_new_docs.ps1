# PowerShell script to ingest new INGRES documentation
Write-Output "🚀 Starting INGRES Documentation Ingestion..."
Write-Output ""

# Show current files
Write-Output "📚 Files found in docs directory:"
Get-ChildItem data\docs | Format-Table Name, Length -AutoSize
Write-Output ""

# Clear old index to ensure fresh ingestion
Write-Output "🧹 Clearing old vector index..."
Remove-Item data\embeddings\faiss.index -Force -ErrorAction SilentlyContinue
Remove-Item data\embeddings\faiss.meta.json -Force -ErrorAction SilentlyContinue
Write-Output "✅ Old index cleared"
Write-Output ""

# Activate virtual environment and run ingestion
Write-Output "⚙️ Processing documents (this may take a few minutes for large PDFs)..."
& .\venv\Scripts\Activate.ps1
python -m scripts.ingest_docs

Write-Output ""
Write-Output "🎉 Document ingestion complete!"
Write-Output ""
Write-Output "📊 Your chatbot now has enhanced INGRES knowledge from:"
Get-ChildItem data\docs -Name
Write-Output ""
Write-Output "🔥 Test your upgraded chatbot at: http://localhost:8080"
Write-Output "💡 Try asking complex INGRES questions!"