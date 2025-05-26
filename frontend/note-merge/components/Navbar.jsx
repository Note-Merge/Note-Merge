import React from "react";

const Navbar = () => {
  return (
    <>
      <div className="flex justify-between items-center text-white/95 py-1 px-4">
        <p className="text-2xl font-bold ml-4">Note Merge</p>
        <div className="mr-4">
          <ul className="flex space-x-5 mr-4 ">
            <li className="text-lg font-semibold hover:text-teal-200 cursor-pointer">
              Home
            </li>
            <li className="text-lg font-semibold hover:text-blue-500 cursor-pointer">
              About
            </li>
            <li className="text-lg font-semibold hover:text-blue-500 cursor-pointer">
              Contact
            </li>
          </ul>
        </div>
      </div>
      <div className="border-1 border-dashed border-gray-600 rounded-md mt-1 mb-4"></div>
    </>
  );
};

export default Navbar;
