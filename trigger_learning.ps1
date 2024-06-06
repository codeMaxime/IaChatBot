# Variables
$unknownPhrasesFile = "C:\Users\theph\Documents\Workspace\IaChatBot\unknown_phrases.txt"
$nluFile = "C:\Users\theph\Documents\Workspace\IaChatBot\data\nlu.yml"

# Lire les nouvelles phrases inconnues
if (Test-Path $unknownPhrasesFile) {
    $newPhrases = Get-Content $unknownPhrasesFile | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
} else {
    $newPhrases = @()
}

if ($newPhrases.Count -gt 0) {
    Write-Output "Found $($newPhrases.Count) new phrases"
    
    # Mettre à jour le fichier nlu.yml
    if (Test-Path $nluFile) {
        Write-Output "Updating $nluFile with new phrases"
        
        $nluContent = Get-Content $nluFile -Raw | ConvertFrom-Yaml
        $intent = "new_intent_$(Get-Random -Minimum 1000 -Maximum 9999)"
        $examples = @()
        
        foreach ($phrase in $newPhrases) {
            $examples += "- $phrase"
        }
        
        $newIntent = @{
            intent = $intent
            examples = $examples -join "`n"
        }
        
        if (-not $nluContent.nlu) {
            $nluContent.nlu = @()
        }
        
        $nluContent.nlu += $newIntent
        
        $nluContent | ConvertTo-Yaml | Out-File -FilePath $nluFile -Encoding UTF8
        
        # Vider le fichier unknown_phrases.txt
        Clear-Content $unknownPhrasesFile
        
        # Entraîner le modèle Rasa
        Write-Output "Training Rasa model"
        & " C:\Users\theph\Documents\Workspace\IaChatBot\iaChatBot64\Scripts\rasa.exe" train
    } else {
        Write-Output "Error: NLU file not found at $nluFile"
    }
} else {
    Write-Output "No new phrases found"
}

Write-Output "Script execution completed."
