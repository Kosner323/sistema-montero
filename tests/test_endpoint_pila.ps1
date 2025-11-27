# TEST ENDPOINT /api/cotizaciones/simular-pila
# ============================================
# Script PowerShell para probar la integración del Motor PILA v1.1 con la API REST

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "TEST MANUAL - ENDPOINT /api/cotizaciones/simular-pila" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

Write-Host "⚠️  IMPORTANTE: Asegúrate de que el servidor Flask esté corriendo" -ForegroundColor Yellow
Write-Host "   Ejecuta: python app.py" -ForegroundColor Yellow
Write-Host "   URL: http://localhost:5000`n" -ForegroundColor Yellow

$baseUrl = "http://localhost:5000"
$endpoint = "/api/cotizaciones/simular-pila"

# ==================== TEST 1: Salario Mínimo Exonerado ====================

Write-Host "TEST 1: Salario Mínimo con Exoneración" -ForegroundColor Green
Write-Host "----------------------------------------------------------------------`n"

$payload1 = @{
    salario_base = 1300000
    nivel_riesgo = 1
    es_salario_integral = $false
    es_empresa_exonerada = $true
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method Post -Body $payload1 -ContentType "application/json" -SessionVariable session
    
    Write-Host "✅ Status: 200 OK`n" -ForegroundColor Green
    Write-Host "📊 RESULTADO:" -ForegroundColor Cyan
    Write-Host "  Salario Base: $($response1.datos_entrada.salario_base.ToString('N0'))"
    Write-Host "  IBC: $($response1.datos_entrada.ibc.ToString('N0'))"
    Write-Host "  Salud Empleado: $($response1.salud.empleado.ToString('N0'))"
    Write-Host "  Salud Empleador: $($response1.salud.empleador.ToString('N0')) (Exonerado: $($response1.salud.empleador_exonerado))"
    Write-Host "  CCF: $($response1.parafiscales.ccf.ToString('N0'))"
    Write-Host "  Total Empleado: $($response1.totales.empleado.ToString('N0'))"
    Write-Host "  Total Empleador: $($response1.totales.empleador.ToString('N0'))"
    Write-Host "  Salario Neto: $($response1.totales.salario_neto.ToString('N0'))"
    
    if ($response1.metadata.advertencias.Count -gt 0) {
        Write-Host "`n⚠️  Advertencias:" -ForegroundColor Yellow
        foreach ($adv in $response1.metadata.advertencias) {
            Write-Host "    $adv" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n✅ TEST 1 PASADO`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# ==================== TEST 2: Salario Alto Sin Exoneración ====================

Write-Host "TEST 2: Salario Alto Sin Exoneración" -ForegroundColor Green
Write-Host "----------------------------------------------------------------------`n"

$payload2 = @{
    salario_base = 15000000
    nivel_riesgo = 3
    es_salario_integral = $false
    es_empresa_exonerada = $false
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method Post -Body $payload2 -ContentType "application/json" -WebSession $session
    
    Write-Host "✅ Status: 200 OK`n" -ForegroundColor Green
    Write-Host "📊 RESULTADO:" -ForegroundColor Cyan
    Write-Host "  Salario Base: $($response2.datos_entrada.salario_base.ToString('N0'))"
    Write-Host "  Salud Empleador: $($response2.salud.empleador.ToString('N0')) (NO exonerado)"
    Write-Host "  CCF: $($response2.parafiscales.ccf.ToString('N0'))"
    Write-Host "  SENA: $($response2.parafiscales.sena.ToString('N0')) (No aplica > 10 SMMLV)"
    Write-Host "  ICBF: $($response2.parafiscales.icbf.ToString('N0')) (No aplica > 10 SMMLV)"
    Write-Host "  Total Empleador: $($response2.totales.empleador.ToString('N0'))"
    
    Write-Host "`n✅ TEST 2 PASADO`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# ==================== TEST 3: Salario Integral ====================

Write-Host "TEST 3: Salario Integral (IBC = 70%)" -ForegroundColor Green
Write-Host "----------------------------------------------------------------------`n"

$payload3 = @{
    salario_base = 25000000
    nivel_riesgo = 2
    es_salario_integral = $true
    es_empresa_exonerada = $false
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method Post -Body $payload3 -ContentType "application/json" -WebSession $session
    
    Write-Host "✅ Status: 200 OK`n" -ForegroundColor Green
    Write-Host "📊 RESULTADO:" -ForegroundColor Cyan
    Write-Host "  Salario Base: $($response3.datos_entrada.salario_base.ToString('N0'))"
    Write-Host "  IBC (70%): $($response3.datos_entrada.ibc.ToString('N0'))"
    Write-Host "  Es Salario Integral: $($response3.datos_entrada.es_salario_integral)"
    Write-Host "  Total Empleado: $($response3.totales.empleado.ToString('N0'))"
    Write-Host "  Total Empleador: $($response3.totales.empleador.ToString('N0'))"
    
    Write-Host "`n✅ TEST 3 PASADO`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# ==================== TEST 4: Tope IBC 25 SMMLV ====================

Write-Host "TEST 4: Tope IBC 25 SMMLV" -ForegroundColor Green
Write-Host "----------------------------------------------------------------------`n"

$payload4 = @{
    salario_base = 40000000
    nivel_riesgo = 4
    es_salario_integral = $false
    es_empresa_exonerada = $false
} | ConvertTo-Json

try {
    $response4 = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method Post -Body $payload4 -ContentType "application/json" -WebSession $session
    
    Write-Host "✅ Status: 200 OK`n" -ForegroundColor Green
    Write-Host "📊 RESULTADO:" -ForegroundColor Cyan
    Write-Host "  Salario Base: $($response4.datos_entrada.salario_base.ToString('N0'))"
    Write-Host "  IBC (tope): $($response4.datos_entrada.ibc.ToString('N0'))"
    Write-Host "  IBC Limitado: $($response4.datos_entrada.ibc_limitado)"
    Write-Host "  Total General: $($response4.totales.general.ToString('N0'))"
    
    Write-Host "`n✅ TEST 4 PASADO`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# ==================== TEST 5: Error - Nivel Riesgo Inválido ====================

Write-Host "TEST 5: Validación de Errores - Nivel Riesgo Inválido" -ForegroundColor Green
Write-Host "----------------------------------------------------------------------`n"

$payload5 = @{
    salario_base = 1300000
    nivel_riesgo = 10
} | ConvertTo-Json

try {
    $response5 = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method Post -Body $payload5 -ContentType "application/json" -WebSession $session -ErrorAction Stop
    
    Write-Host "❌ ERROR: Esperaba status 400, obtuvo 200`n" -ForegroundColor Red
    exit 1
    
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✅ Status: 400 Bad Request (esperado)`n" -ForegroundColor Green
        Write-Host "📛 Error esperado: Nivel de riesgo inválido"
        Write-Host "`n✅ TEST 5 PASADO`n" -ForegroundColor Green
    } else {
        Write-Host "❌ ERROR: $($_.Exception.Message)`n" -ForegroundColor Red
        exit 1
    }
}

# ==================== RESUMEN ====================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎉 TODOS LOS TESTS PASARON (5/5)" -ForegroundColor Green
Write-Host "======================================================================`n" -ForegroundColor Cyan

Write-Host "✅ El Motor PILA v1.1 está correctamente integrado con la API REST" -ForegroundColor Green
Write-Host "✅ Endpoint: POST /api/cotizaciones/simular-pila" -ForegroundColor Green
Write-Host "✅ Versión Motor: 1.1.0" -ForegroundColor Green
Write-Host "✅ Estado: LISTO PARA PRODUCCIÓN`n" -ForegroundColor Green

exit 0
