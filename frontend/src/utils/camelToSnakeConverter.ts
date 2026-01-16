/**
 * 将驼峰命名的字符串转换为小写加下划线格式
 * 修复：排除开头的大写字母，避免开头多出下划线
 * @param str 驼峰命名的字符串（支持大驼峰/小驼峰）
 * @returns 小写加下划线格式的字符串
 */
export function camelToSnake(str: string): string {
  // (?<!^) 断言：不是字符串开头的位置
  // 只对非开头的大写字母添加下划线，最后统一转小写
  return str.replace(/(?<!^)[A-Z]/g, (letter) => `_${letter.toLowerCase()}`).toLowerCase();
}

/**
 * 将对象中的所有键从驼峰命名转换为小写加下划线格式
 * @param obj 要转换的对象
 * @returns 键已转换的对象
 */
export function convertKeysToSnake(obj: any): any {
  if (obj === null || typeof obj !== 'object' || obj instanceof Date || obj instanceof File) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToSnake(item));
  }

  const convertedObj: any = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const snakeKey = camelToSnake(key);
      convertedObj[snakeKey] = convertKeysToSnake(obj[key]);
    }
  }

  return convertedObj;
}

/**
 * 将对象中的所有键从小写加下划线格式转换为驼峰命名
 * @param obj 要转换的对象
 * @returns 键已转换的对象
 */
export function convertKeysToCamel(obj: any): any {
  if (obj === null || typeof obj !== 'object' || obj instanceof Date || obj instanceof File) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToCamel(item));
  }

  const convertedObj: any = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      // 将下划线分隔的字符串转换为驼峰命名（小驼峰）
      const camelKey = key.replace(/_([a-z])/g, (match, char) => char.toUpperCase());
      convertedObj[camelKey] = convertKeysToCamel(obj[key]);
    }
  }

  return convertedObj;
}