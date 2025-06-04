import { useId,useState, ChangeEvent,useEffect } from "react"

import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

interface TextBoxProps {
  onTextChange: (text: string)=> void;
}

export default function TextBox( {onTextChange }: TextBoxProps) {
  const id = useId()
  const [text, setText] = useState("");

  useEffect(()=> {
    onTextChange(text);
  },[text]);

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  return (
    <div className="flex justify-center my-3 px-3">
      <div className="flex flex-col items-center lg:-translate-x-1/1">
        <Label className="text-white mr-auto mt-4 mb-1" htmlFor={id}>Additional Notes</Label>
        <Textarea
          id={id}
          className="bg-gray-800 border-transparent shadow-none mt-2 w-64"
          placeholder="Add any additional notes or context here..."
          rows={6}
          value={text}
          onChange={handleChange}
        />
      </div>
    </div>
  )
}
