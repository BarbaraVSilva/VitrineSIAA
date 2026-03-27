@echo off
echo === Iniciando Atualização do Git ===

:: Tenta renomear a branch para Main ===
git branch -m main

:: Adiciona todas as alterações ===
git add .

:: Commita as alterações ===
set datetime=%date% %time%
git commit -m "Atualização do Git %datetime%"

:: Envia as alterações para o repositório ===
git pull origin main --rebase -X ours

:: Envia as alterações para o repositório ===
git push origin main --force

:: Exibe uma mensagem de sucesso ===
echo === Atualização do Git concluída com sucesso ===
pause