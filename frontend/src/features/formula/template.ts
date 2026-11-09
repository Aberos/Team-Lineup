export const FORMULA_TEMPLATE = `function overall(notas, funcoes, principal)
  local pesos = { VEL = 1, FIN = 1, PAS = 1, DRI = 1, DEF = 1, ["FÍS"] = 1 }
  if principal == "DEF" then
    pesos.DEF = 3
    pesos["FÍS"] = 2
  elseif principal == "ATK" then
    pesos.FIN = 3
    pesos.VEL = 2
  end
  local soma, total = 0, 0
  for sigla, peso in pairs(pesos) do
    if notas[sigla] then
      soma = soma + notas[sigla] * peso
      total = total + peso
    end
  end
  if total == 0 then
    return nil
  end
  return soma / total
end
`
