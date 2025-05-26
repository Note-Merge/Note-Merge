import React from 'react'

const FileUpload = () => {
  return (
    <>
    <div className='flex flex-col space-y-4 justify-between items-center text-white/85'>
        <p className='text-3xl text-center font-semibold '>Merge Your Notes</p>
        <div className='flex justify-center items-center'>
            <p >Combine multiple notes into a single coherent document</p>
        </div>
    </div>
    <div className='pt-4 mt-4 ml-4 pl-4 text-white/90 flex flex-col space-y-2'>
      <span className='text-left pl-3 font-medium size-md  ml-1'>Select model</span>
      <select className='bg-[#1a1b1b] text-white/90 border-2 border-gray-600 rounded-md p-2 ml-1 mr-auto'>
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        <option value="gpt-4">GPT-4</option>
      </select>
    </div>
    </>
  )
}

export default FileUpload;