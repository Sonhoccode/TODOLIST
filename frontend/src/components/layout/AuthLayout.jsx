// components/AuthLayout.jsx
export default function AuthLayout({ title, tagline, children, imgAlt = "Preview" }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b w-full h-[72px]">
        <div className="max-w-6xl mx-auto h-full px-6 flex items-center justify-between">
          <div className="text-2xl font-bold">TODO</div>
          <p className="text-sm md:text-base text-gray-600">{tagline}</p>
        </div>
      </header>

      {/* Body */}
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-8 items-center min-h-[calc(100vh-72px)]">
          {/* Ảnh (ẩn trên mobile) */}
          <div className="hidden md:flex items-center justify-center">
            <div className="w-full max-w-md aspect-[4/3]">
              <img
                src="/image/review.png"
                alt={imgAlt}
                className="w-full h-full object-contain rounded-2xl shadow"
              />
            </div>
          </div>

          {/* Form/Card */}
          <div className="flex items-center justify-center">
            <div className="w-full max-w-md bg-white rounded-2xl shadow p-6 md:p-8">
              <h1 className="text-2xl font-bold mb-6 text-center">{title}</h1>
              {children}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
