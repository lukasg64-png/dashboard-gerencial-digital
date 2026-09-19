# ==============================================================================
# FARMÁCIAS SÃO JOÃO — AGENDADOR AUTOMÁTICO DO DASHBOARD GERENCIAL
# Registra tarefa no Windows Task Scheduler para rodar todo dia às 06:30 da manhã
# ==============================================================================

$TaskName = "Atualizar_Dashboard_Gerencial_FSJ"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatPath = Join-Path $ScriptDir "atualizar_dashboard.bat"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURANDO AGENDAMENTO AUTOMÁTICO NO WINDOWS TASK SCHEDULER" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Tarefa: $TaskName"
Write-Host "Script: $BatPath"
Write-Host "Horário: Diariamente às 07:20 AM"

# Verifica se a tarefa já existe e remove para recriar limpa
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Removendo agendamento anterior existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Define a Ação (executar atualizar_dashboard.bat com modo não-interativo)
$Action = New-ScheduledTaskAction -Execute $BatPath -Argument "--unattended" -WorkingDirectory $ScriptDir

# Define o Gatilho (diário às 07:20)
$Trigger = New-ScheduledTaskTrigger -Daily -At "07:20"

# Configurações de Resiliência
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20)

# Registra a Tarefa
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description "Atualização automática diária matinal do Dashboard Gerencial Digital e Figital das Farmácias São João" `
        -ErrorAction Stop | Out-Null

    Write-Host "`n✅ Agendamento registrado com sucesso!" -ForegroundColor Green
    Write-Host "A rotina executará automaticamente todo dia de manhã cedo às 06:30." -ForegroundColor Green
} catch {
    Write-Host "`n⚠️ Não foi possível registrar como Administrador diretamente ($($_.Exception.Message))." -ForegroundColor Yellow
    Write-Host "Para registrar, abra o PowerShell como Administrador e execute este script." -ForegroundColor Yellow
}
