"use client";
import { useState } from "react";
import Particles from "@/components/Particles/Particles";
import TextBox from "@/components/TextBox";
import Uploader from "@/components/Uploader";
import { useDarkModeStore } from "@/store/useDarkModeStore";

export default function Home() {


  const { isDarkMode, toggleDarkMode } = useDarkModeStore();
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [selectedModel,setSelectedModel] = useState<string>("LSTM");
  const [additionalNotes, setAdditionalNotes] = useState<string>("");

  const handleMergeNotes = async () =>{
    const formData = new FormData();
    uploadedFiles.forEach((file)=> {
      formData.append("files", file);
    });
    formData.append("model", selectedModel);
    formData.append("notes", additionalNotes);

    try {
      const response = await fetch("http://localhost:8000/merge-notes/",
        {
          method: "POST",
          body: formData,
        });
      
      const data = await response.json();
      console.log("Merge response:", data.result);
    }catch(error) {
      console.error("Error merging notes:", error);
    }
  }

  console.log("Dark mode is", isDarkMode);
  return (
    <>
      <div className="relative min-h-screen bg-neutral-900 overflow-hidden">
        <div className="absolute inset-0 z-0 pointer-events-none">
          <Particles />
        </div>
        <div className="flex justify-between items-center text-white/95 py-1 px-4">
        <p className="text-2xl font-bold ml-4">Note Merge</p>
        

        {/* Dark Mode Button */}
        <div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input className="sr-only peer" value="" type="checkbox" />
            <div className="w-24 h-12 rounded-full ring-0 peer duration-500 outline-none bg-gray-200 overflow-hidden before:flex before:items-center before:justify-center after:flex after:items-center after:justify-center before:content-['☀️'] before:absolute before:h-10 before:w-10 before:top-1/2 before:bg-white before:rounded-full before:left-1 before:-translate-y-1/2 before:transition-all before:duration-700 peer-checked:before:opacity-0 peer-checked:before:rotate-90 peer-checked:before:-translate-y-full shadow-lg shadow-gray-400 peer-checked:shadow-lg peer-checked:shadow-gray-700 peer-checked:bg-[#383838] after:content-['🌑'] after:absolute after:bg-[#1d1d1d] after:rounded-full after:top-[4px] after:right-1 after:translate-y-full after:w-10 after:h-10 after:opacity-0 after:transition-all after:duration-700 peer-checked:after:opacity-100 peer-checked:after:rotate-180 peer-checked:after:translate-y-0"></div>
          </label>
        </div>
      </div>
    
      <div className="border-1 border-dashed border-gray-600 rounded-md mt-1 mb-4"></div>


        {/* <FileUpload /> */}
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
                <select className='bg-[#1a1b1b] text-white/90 border-2 border-gray-600 rounded-md p-2 ml-1 mr-auto w-fit' value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                  <option value="LSTM">LSTM</option>
                  <option value="Transformer">Transformer</option>
                </select>
              </div>
              {/* Uploader */}
              <Uploader onFilesSelected = {setUploadedFiles}/>
                  {uploadedFiles.length>0?<p className="text-white/85">Number of files uploaded: {uploadedFiles.length}</p>:<></>}
              
            </div>
        <TextBox onTextChange= {setAdditionalNotes} />
        {additionalNotes && <div className="mt-4 text-white">
        <h2 className="text-lg font-semibold">Preview Notes:</h2>
        <p>{additionalNotes}</p>
      </div>}
        <div>
          <div className="flex justify-center sm:justify-start sm:mx-auto  flex-col max-w-3xl mt-4 mb-4 sm:w-full">
            <div className="relative group">
              <button className="relative inline-block p-px font-semibold leading-6 text-white bg-gray-800 shadow-2xl cursor-pointer rounded-xl shadow-zinc-900 transition-transform duration-300 ease-in-out hover:scale-105 active:scale-95">
                <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-400 via-blue-500 to-purple-500 p-[2px] opacity-0 transition-opacity duration-500 group-hover:opacity-100"></span>
                <span className="relative z-10 block px-3 py-3 rounded-xl bg-gray-950">
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="transition-all duration-500 group-hover:translate-x-1">
                      Merge Notes
                    </span>
                  </div>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
