/**
 * Compara dois objetos JSON e retorna as diferenças
 * @param {Object} json1 - Primeiro JSON
 * @param {Object} json2 - Segundo JSON
 * @returns {Object} - Objeto com diferenças mapeadas
 */
export function compareJSONs(json1, json2) {
  const differences = {
    added: [],         // Chaves que existem apenas em json2
    removed: [],       // Chaves que existem apenas em json1
    modified: [],      // Chaves que existem em ambos mas com valores diferentes (mantido para compatibilidade)
    keyChanged: [],    // Chaves que mudaram de nome
    emptyValue: [],    // Chaves com valores vazios ""
    unchanged: []      // Chaves que são iguais
  }

  // Função recursiva para comparar objetos
  function compareObjects(obj1, obj2, path = '') {
    const keys1 = Object.keys(obj1 || {})
    const keys2 = Object.keys(obj2 || {})
    const allKeys = new Set([...keys1, ...keys2])

    // Detectar mudanças de chave (chaves que mudaram de nome mas têm valores similares)
    const keyMapping = findKeyMappings(obj1, obj2, path)

    allKeys.forEach(key => {
      const currentPath = path ? `${path}.${key}` : key
      const val1 = obj1?.[key]
      const val2 = obj2?.[key]

      // Verificar se a chave mudou de nome
      const keyChange = keyMapping.find(m => m.newKey === key || m.oldKey === key)
      if (keyChange && keyChange.newKey === key && !(keyChange.oldKey in (obj2 || {}))) {
        // Esta é uma nova chave que veio de uma chave antiga
        differences.keyChanged.push({
          path: currentPath,
          oldPath: keyChange.oldPath,
          oldKey: keyChange.oldKey,
          newKey: key,
          oldValue: keyChange.oldValue,
          newValue: val2,
          type: getValueType(val2)
        })
        return
      }

      // Chave existe apenas em json2
      if (!(key in (obj1 || {}))) {
        // Verificar se é uma mudança de chave ou realmente uma adição
        const isKeyChange = keyMapping.some(m => m.newKey === key)
        if (!isKeyChange) {
          differences.added.push({
            path: currentPath,
            value: val2,
            type: getValueType(val2),
            isEmpty: val2 === ''
          })
        }
      }
      // Chave existe apenas em json1
      else if (!(key in (obj2 || {}))) {
        // Verificar se é uma mudança de chave ou realmente uma remoção
        const isKeyChange = keyMapping.some(m => m.oldKey === key)
        if (!isKeyChange) {
          differences.removed.push({
            path: currentPath,
            value: val1,
            type: getValueType(val1),
            isEmpty: val1 === ''
          })
        }
      }
      // Chave existe em ambos
      else {
        // Verificar se o valor está vazio primeiro
        if (val2 === '' || val1 === '') {
          differences.emptyValue.push({
            path: currentPath,
            oldValue: val1,
            newValue: val2,
            oldType: getValueType(val1),
            newType: getValueType(val2),
            isEmptyInFile1: val1 === '',
            isEmptyInFile2: val2 === ''
          })
        } else if (typeof val1 === 'object' && val1 !== null && !Array.isArray(val1) &&
            typeof val2 === 'object' && val2 !== null && !Array.isArray(val2)) {
          // Ambos são objetos, comparar recursivamente
          compareObjects(val1, val2, currentPath)
        } else if (JSON.stringify(val1) !== JSON.stringify(val2)) {
          // Valores diferentes (apenas se não forem vazios)
          differences.modified.push({
            path: currentPath,
            oldValue: val1,
            newValue: val2,
            oldType: getValueType(val1),
            newType: getValueType(val2)
          })
        } else {
          // Valores iguais
          differences.unchanged.push({
            path: currentPath,
            value: val1
          })
        }
      }
    })
  }

  // Função para encontrar mapeamentos de chaves que mudaram de nome
  function findKeyMappings(obj1, obj2, path = '') {
    const mappings = []
    const keys1 = Object.keys(obj1 || {})
    const keys2 = Object.keys(obj2 || {})

    // Para cada chave em obj1 que não existe em obj2, tentar encontrar uma correspondência em obj2
    keys1.forEach(key1 => {
      if (!(key1 in (obj2 || {}))) {
        const val1 = obj1[key1]
        // Procurar em obj2 por uma chave com valor similar
        keys2.forEach(key2 => {
          if (!(key2 in (obj1 || {}))) {
            const val2 = obj2[key2]
            // Se os valores são iguais ou muito similares, pode ser uma mudança de chave
            if (JSON.stringify(val1) === JSON.stringify(val2)) {
              mappings.push({
                oldKey: key1,
                newKey: key2,
                oldPath: path ? `${path}.${key1}` : key1,
                newPath: path ? `${path}.${key2}` : key2,
                oldValue: val1,
                newValue: val2
              })
            }
          }
        })
      }
    })

    return mappings
  }

  compareObjects(json1, json2)
  return differences
}

/**
 * Obtém o tipo de um valor
 */
function getValueType(value) {
  if (value === null) return 'null'
  if (Array.isArray(value)) return 'array'
  return typeof value
}

/**
 * Formata um objeto JSON para exibição linha por linha
 * @param {Object} obj - Objeto JSON
 * @param {Object} differences - Objeto com diferenças
 * @param {string} side - 'left' ou 'right'
 * @returns {Array} - Array de linhas formatadas
 */
export function formatJSONForDisplay(obj, differences, side) {
  const lines = []
  
  // Criar mapas de diferenças por path
  const addedPaths = new Set(differences.added.map(d => d.path))
  const removedPaths = new Set(differences.removed.map(d => d.path))
  const modifiedPaths = new Set(differences.modified.map(d => d.path))
  const keyChangedPaths = new Set(differences.keyChanged.map(d => d.path))
  const keyChangedOldPaths = new Set(differences.keyChanged.map(d => d.oldPath))
  const emptyValuePaths = new Set(differences.emptyValue.map(d => d.path))
  const unchangedPaths = new Set(differences.unchanged.map(d => d.path))

  // Obter todos os paths do objeto atual
  const flatObj = flattenObject(obj)
  const objPaths = new Set(Object.keys(flatObj))

  // Combinar todos os paths (do objeto atual + diferenças)
  const allPaths = new Set([
    ...Array.from(objPaths),
    ...Array.from(addedPaths),
    ...Array.from(removedPaths),
    ...Array.from(modifiedPaths),
    ...Array.from(keyChangedPaths),
    ...Array.from(keyChangedOldPaths),
    ...Array.from(emptyValuePaths),
    ...Array.from(unchangedPaths)
  ])

  // Ordenar paths para exibição consistente
  const sortedPaths = Array.from(allPaths).sort()

  sortedPaths.forEach(path => {
    let status = 'unchanged'
    let value = null

    if (side === 'left') {
      if (keyChangedOldPaths.has(path)) {
        status = 'keyChanged'
        const keyChange = differences.keyChanged.find(d => d.oldPath === path)
        value = keyChange?.oldValue
      } else if (removedPaths.has(path)) {
        status = 'removed'
        value = differences.removed.find(d => d.path === path)?.value
      } else if (emptyValuePaths.has(path)) {
        status = 'emptyValue'
        value = differences.emptyValue.find(d => d.path === path)?.oldValue
      } else if (modifiedPaths.has(path)) {
        status = 'modified'
        value = differences.modified.find(d => d.path === path)?.oldValue
      } else if (unchangedPaths.has(path)) {
        status = 'unchanged'
        value = differences.unchanged.find(d => d.path === path)?.value
      } else if (objPaths.has(path)) {
        // Path existe no objeto mas não está nas diferenças (pode ser um objeto aninhado)
        value = flatObj[path]
        status = 'unchanged'
      }
    } else { // right
      if (keyChangedPaths.has(path)) {
        status = 'keyChanged'
        const keyChange = differences.keyChanged.find(d => d.path === path)
        value = keyChange?.newValue
      } else if (addedPaths.has(path)) {
        status = 'added'
        value = differences.added.find(d => d.path === path)?.value
      } else if (emptyValuePaths.has(path)) {
        status = 'emptyValue'
        value = differences.emptyValue.find(d => d.path === path)?.newValue
      } else if (modifiedPaths.has(path)) {
        status = 'modified'
        value = differences.modified.find(d => d.path === path)?.newValue
      } else if (unchangedPaths.has(path)) {
        status = 'unchanged'
        value = differences.unchanged.find(d => d.path === path)?.value
      } else if (objPaths.has(path)) {
        // Path existe no objeto mas não está nas diferenças
        value = flatObj[path]
        status = 'unchanged'
      }
    }

    if (value !== undefined && value !== null) {
      lines.push({
        path,
        value,
        status,
        display: formatPathValue(path, value)
      })
    }
  })

  return lines
}

/**
 * Achata um objeto aninhado em um objeto plano
 */
function flattenObject(obj, prefix = '', result = {}) {
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const newKey = prefix ? `${prefix}.${key}` : key
      if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
        flattenObject(obj[key], newKey, result)
      } else {
        result[newKey] = obj[key]
      }
    }
  }
  return result
}

/**
 * Formata path e valor para exibição
 */
function formatPathValue(path, value) {
  const parts = path.split('.')
  const indent = (parts.length - 1) * 2
  const indentStr = ' '.repeat(Math.max(0, indent))
  const key = parts[parts.length - 1]
  
  let valueStr = ''
  if (value === null) {
    valueStr = 'null'
  } else if (typeof value === 'string') {
    // Escapar aspas e quebras de linha
    const escaped = value
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t')
    valueStr = `"${escaped}"`
  } else if (Array.isArray(value)) {
    valueStr = JSON.stringify(value, null, 2)
      .split('\n')
      .map((line, idx) => idx === 0 ? line : indentStr + line)
      .join('\n')
  } else if (typeof value === 'object') {
    valueStr = JSON.stringify(value, null, 2)
      .split('\n')
      .map((line, idx) => idx === 0 ? line : indentStr + line)
      .join('\n')
  } else {
    valueStr = String(value)
  }

  return `${indentStr}"${key}": ${valueStr}`
}

