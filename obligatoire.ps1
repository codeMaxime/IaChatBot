# Sauvegarde la politique d'exécution actuelle
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser

# Définit la politique d'exécution pour permettre l'exécution de scripts
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

# Active l'environnement virtuel
. C:\Users\theph\Documents\Workspace\IaChatBot\iaChatBot64\Scripts\Activate.ps1

# Affiche un message
Write-Host "Environnement activé. Appuyez sur une touche pour quitter et rétablir la politique de sécurité."
Read-Host

# Rétablit la politique d'exécution originale
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy $currentPolicy -Force
