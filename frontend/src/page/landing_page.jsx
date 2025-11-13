import React from "react";

export default function LandingPage() {
  return (
    <>
      <header className="layout-container sticky top-0 z-50 bg-white w-full h-[62px] p-1 flex items-center justify-between">
        {/* header trái */}
        <div className="flex w-3/4 h-full items-center justify-start px-8">
          <span className="flex items-center justify-center px-4 py-2 rounded-full bg-gray-900 text-white text-sm font-bold">
            TODO
          </span>
        </div>
        {/* header phải */}
        <div className="flex h-full w-1/4 items-center justify-end gap-4 px-8">
          <button
            className="px-[30px] py-[8px] border border-transparent bg-black text-white rounded-lg 
             hover:border-black hover:bg-white hover:text-black transition"
            onClick={() => {
              window.location.href = "/login";
            }}
          >
            Sign In
          </button>
          <button
            className="ml-4 px-[30px] py-[8px] border border-transparent bg-black text-white rounded-lg 
             hover:border-black hover:bg-white hover:text-black transition"
            onClick={() => {
              window.location.href = "/register";
            }}
          >
            Sign Up
          </button>
        </div>
      </header>
      <main>
        <div className="layout-container w-full h-full flex flex-col items-center justify-between">
          {/* welcome */}
          <div className="layout-container w-full min-h-[calc(100vh-72px)] flex items-center justify-between">
            {/* Welcome left */}
             <div className="flex w-2/5 flex-col items-center justify-center px-8 text-center
                  -mt-6 md:-mt-10">
                <h1 className="text-4xl font-bold mb-4 leading-tight">
                  Welcome to the TODO App
                </h1>
              <p className="text-lg text-gray-600 max-w-md">
                This is a simple TODO application built by Group 10 of the Python
                Programming course. We built it using <span className="font-semibold text-black">Django</span> + <span className="font-semibold text-sky-600">ReactJS</span>.
              </p>

              <button
                className="mt-6 px-12 py-6 bg-gray-900 text-white rounded-lg hover:bg-black transition"
                onClick={() => {
                  window.location.href = "/login";
                }}
              >
                Get Started
              </button>

            </div>

            <div className="flex w-3/5 items-center justify-center px-8">
              <img
                src="/image/review.png"
                alt="Review"
                className="object-contain w-full max-h-[60vh] rounded-xl border border-gray-300 shadow-lg"
              />
            </div>
          </div>
          {/* bot body */}

        <div>
          <h1 className="text-center text-gray-500 text-sm py-4">
            © 2025 Group 10 - Python Programming Course
          </h1>
        </div>
        </div>
      </main>
    </>
  );
}