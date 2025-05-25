import React from 'react'


const Navbar = () => {
  return (
    <div className='flex justify-between items-center text-black p-4'>
    <p className='text-3xl font-bold ml-4'>Note Merge</p>'
    <div className='mr-4'>
          <ul className='flex space-x-5 mr-4 '>
            <li className='text-lg font-semibold hover:text-blue-500 cursor-pointer'>Home</li>
            <li className='text-lg font-semibold hover:text-blue-500 cursor-pointer'>About</li>
            <li className='text-lg font-semibold hover:text-blue-500 cursor-pointer'>Contact</li>
          </ul>
    </div>
    </div>
  )
}

export default Navbar