import { useId } from "react"

import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export default function TextBox() {
  const id = useId()
  return (
    <div className="flex justify-center my-3 px-3">
      <div className="flex flex-col items-center lg:-translate-x-1/1">
        <Label className="text-white/85 mr-auto mt-4 mb-1" htmlFor={id}>Additional Notes</Label>
        <Textarea
          id={id}
          className="bg-muted border-transparent shadow-none mt-2 w-64"
          placeholder="Add any additional notes or context here..."
          rows={6}
        />
      </div>
    </div>
  )
}
