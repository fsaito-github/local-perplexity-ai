@echo off
REM Script para iniciar o Foundry e executar testes da migração

echo.
echo ===============================================
echo   AZURE AI FOUNDRY LOCAL - INICIO DO SERVIDOR
echo ===============================================
echo.

REM Verificar se o Foundry está instalado
foundry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Azure AI Foundry Local nao encontrado!
    echo Instale com: winget install Microsoft.AzureAIFoundryLocal
    pause
    exit /b 1
)

echo [OK] Foundry instalado
echo.

REM Verificar modelos
echo Verificando modelos...
foundry model ls | findstr "phi-4-mini deepseek-r1-7b" >nul
if %errorlevel% neq 0 (
    echo AVISO: Modelos nao encontrados
    echo Execute: 
    echo   foundry model download phi-4-mini --device gpu
    echo   foundry model download deepseek-r1-7b --device gpu
)

echo [OK] Modelos disponiveis
echo.

REM Iniciar servidor
echo Iniciando servidor Foundry na porta 5272...
echo.
foundry serve --port 5272

REM Se o servidor foi interrompido
echo.
echo Servidor Foundry foi parado.
pause
