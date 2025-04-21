export function toTitleCase(str: string) {
  let result = str.replace(
    /\w\S*/g,
    (text) => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase(),
  )
  if (result === 'Not Start') return 'Not Started'
  return result
}
