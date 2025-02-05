import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export function useScroll() {
  const atBottom = ref(false) // Reactive state to track if user is at the bottom

  function scrollToTop(): void {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  function scrollToBottom(): void {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth',
    })
  }

  function scrollToSelectedCard(index: number | null): void {
    if (index !== null) {
      nextTick(() => {
        const cardElement = document.querySelectorAll('.screening-card')[
          index
        ] as HTMLElement
        if (cardElement) {
          const navbarHeight = 58
          const cardRect = cardElement.getBoundingClientRect()
          const scrollPosition = window.scrollY + cardRect.top - navbarHeight

          window.scrollTo({
            top: scrollPosition,
            behavior: 'smooth',
          })
        }
      })
    }
  }

  function updateAtBottom(): void {
    const scrollPosition = window.scrollY + window.innerHeight
    const totalHeight = document.documentElement.scrollHeight
    atBottom.value = scrollPosition >= totalHeight
  }

  onMounted(() => {
    window.addEventListener('scroll', updateAtBottom)
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', updateAtBottom)
  })

  return {
    scrollToTop,
    scrollToBottom,
    scrollToSelectedCard,
    isAtBottom: atBottom,
  }
}
