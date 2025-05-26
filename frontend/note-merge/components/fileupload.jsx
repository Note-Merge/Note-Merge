import React from 'react';
import Uploader from './Uploader';

const FileUpload = () => {
  return (
    <div className='flex flex-col items-center w-full px-4'>
      {/* Header */}
      <div className='flex flex-col space-y-4 justify-between items-center text-white/85 max-w-3xl w-full'>
        <p className='text-3xl text-center font-semibold'>Merge Your Notes</p>
        <div className='flex justify-center items-center'>
          <p>Combine multiple notes into a single coherent document</p>
        </div>
      </div>

      {/* Model Selector (left-aligned within centered box) */}
      <div className='text-white/90 flex flex-col space-y-2 w-full max-w-3xl mt-6 mb-4'>
        <span className='text-left pl-3 font-medium size-md ml-1'>Select model</span>
        <select className='bg-[#1a1b1b] text-white/90 border-2 border-gray-600 rounded-md p-2 ml-1 mr-auto w-fit'>
          <option value="gpt-3.5-turbo">LSTM</option>
          <option value="gpt-4">Transformer</option>
        </select>
      </div>

      {/* Uploader */}
      <Uploader />
    </div>
  );
};

export default FileUpload;
