import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"

interface LoadingPopupProps {
  isOpen: boolean
  progress: number
  message: string
}

export function LoadingPopup({ isOpen, progress, message }: LoadingPopupProps) {
  return (
    <Dialog open={isOpen}>
      <DialogContent className="sm:max-w-[425px]">
        <div className="text-center">
          <h3 className="text-lg font-medium leading-6 text-gray-900 mb-5">Analyzing Your Document</h3>
          <Progress value={progress} className="w-full mb-4" />
          <p className="text-sm text-gray-500">{message}</p>
        </div>
      </DialogContent>
    </Dialog>
  )
}

