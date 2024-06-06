# Sauvegarde la politique d'ex�cution actuelle
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser

# D�finit la politique d'ex�cution pour permettre l'ex�cution de scripts
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

# Active l'environnement virtuel
. C:\Users\theph\Documents\Workspace\IaChatBot\iaChatBot64\Scripts\Activate.ps1

# Affiche un message
Write-Host "Environnement activ�. Appuyez sur une touche pour quitter et r�tablir la politique de s�curit�."
Read-Host

# R�tablit la politique d'ex�cution originale
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy $currentPolicy -Force
