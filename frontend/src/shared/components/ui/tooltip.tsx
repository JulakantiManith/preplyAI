import * as React from "react"

import { cn } from "@/shared/lib/utils"

interface TooltipProviderProps {
  children: React.ReactNode
  delayDuration?: number
}

interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  side?: "top" | "right" | "bottom" | "left"
  className?: string
}

const TooltipContext = React.createContext<{
  delayDuration: number
}>({ delayDuration: 300 })

function TooltipProvider({
  children,
  delayDuration = 300,
}: TooltipProviderProps) {
  return (
    <TooltipContext.Provider value={{ delayDuration }}>
      {children}
    </TooltipContext.Provider>
  )
}

function Tooltip({ children, content, side = "top", className }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const { delayDuration } = React.useContext(TooltipContext)
  const timeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null)

  function handleMouseEnter() {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)
    }, delayDuration)
  }

  function handleMouseLeave() {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    setIsVisible(false)
  }

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  }

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
    >
      {children}
      {isVisible && (
        <div
          role="tooltip"
          className={cn(
            "absolute z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95",
            positionClasses[side],
            className
          )}
        >
          {content}
        </div>
      )}
    </div>
  )
}

export { Tooltip, TooltipProvider }
