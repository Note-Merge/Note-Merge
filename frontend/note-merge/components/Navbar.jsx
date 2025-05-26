import { useDarkModeStore } from "@/store/useDarkModeStore";
import React from "react";

const Navbar = () => {
  const {isDarkMode, setIsDarkMode} = useDarkModeStore();
  return (
    <>
      <div className="flex justify-between items-center text-white/95 py-1 px-4">
        <p className="text-2xl font-bold ml-4">Note Merge</p>
        <div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input className="sr-only peer" value="" type="checkbox" />
            <div className="w-24 h-12 rounded-full ring-0 peer duration-500 outline-none bg-gray-200 overflow-hidden before:flex before:items-center before:justify-center after:flex after:items-center after:justify-center before:content-['☀️'] before:absolute before:h-10 before:w-10 before:top-1/2 before:bg-white before:rounded-full before:left-1 before:-translate-y-1/2 before:transition-all before:duration-700 peer-checked:before:opacity-0 peer-checked:before:rotate-90 peer-checked:before:-translate-y-full shadow-lg shadow-gray-400 peer-checked:shadow-lg peer-checked:shadow-gray-700 peer-checked:bg-[#383838] after:content-['🌑'] after:absolute after:bg-[#1d1d1d] after:rounded-full after:top-[4px] after:right-1 after:translate-y-full after:w-10 after:h-10 after:opacity-0 after:transition-all after:duration-700 peer-checked:after:opacity-100 peer-checked:after:rotate-180 peer-checked:after:translate-y-0"></div>
          </label>
        </div>
      </div>
      <div className="border-1 border-dashed border-gray-600 rounded-md mt-1 mb-4"></div>
    </>
  );
};

export default Navbar;
