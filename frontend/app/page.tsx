'use client';

import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ICCDocument {
  id: number;
  code: string;
  year: number;
  title: string;
  state: string | null;
  base_url: string;
}

interface ICCSection {
  id: number;
  section_number: string;
  title: string;
  chapter: number;
  url: string;
  description: string;
  document_id: number;
  document: ICCDocument;
}

interface SearchResult {
  csi_code: {
    id: number;
    code: string;
    division: number;
    title: string;
    description: string;
  };
  icc_sections: ICCSection[];
  total_results: number;
}

export default function Home() {
  const [csiCode, setCsiCode] = useState('');
  const [selectedDocument, setSelectedDocument] = useState('');
  const [availableDocuments, setAvailableDocuments] = useState<ICCDocument[]>([]);
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch available ICC documents on mount
  useEffect(() => {
    fetch(`${API_URL}/api/icc-documents`)
      .then(res => res.json())
      .then((docs: ICCDocument[]) => {
        setAvailableDocuments(docs);
        // Default to first document if available
        if (docs.length > 0) {
          setSelectedDocument(`${docs[0].code}|${docs[0].year}`);
        }
      })
      .catch(err => console.error('Failed to fetch ICC documents:', err));
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);

    // Parse selected document (format: "IPC|2018")
    const [docCode, docYear] = selectedDocument.split('|');

    try {
      const response = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          csi_code: csiCode,
          icc_document: docCode || null,
          year: docYear ? parseInt(docYear) : null,
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError('CSI code not found. Please try another code.');
        } else {
          setError('An error occurred. Please try again.');
        }
        return;
      }

      const data: SearchResult = await response.json();
      setResults(data);
    } catch (err) {
      setError('Failed to connect to the server. Please ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50 to-neutral-100">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">CSI to ICC Code Mapper</h1>
              <p className="text-sm text-neutral-600">MasterFormat to Building Code Reference For Student and Educational use</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="bg-white rounded-xl shadow-md border border-neutral-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">Search CSI Code</h2>

          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* CSI Code Input */}
              <div>
                <label htmlFor="csi-code" className="block text-sm font-medium text-neutral-700 mb-1">
                  CSI Code *
                </label>
                <input
                  id="csi-code"
                  type="text"
                  value={csiCode}
                  onChange={(e) => setCsiCode(e.target.value)}
                  placeholder="e.g., 03 30 00"
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
                  required
                />
              </div>

              {/* ICC Document Selection */}
              <div>
                <label htmlFor="icc-document" className="block text-sm font-medium text-neutral-700 mb-1">
                  ICC Document
                </label>
                <select
                  id="icc-document"
                  value={selectedDocument}
                  onChange={(e) => setSelectedDocument(e.target.value)}
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition bg-white"
                >
                  {availableDocuments.map((doc) => (
                    <option key={doc.id} value={`${doc.code}|${doc.year}`}>
                      {doc.code} {doc.year}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Search Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full md:w-auto px-8 py-2.5 bg-primary-600 hover:bg-primary-700 disabled:bg-neutral-400 text-white font-medium rounded-lg transition duration-200 flex items-center justify-center space-x-2 shadow-sm"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Search</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-8 flex items-start space-x-2">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            {/* CSI Code Info */}
            <div className="bg-white rounded-xl shadow-md border border-neutral-200 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="inline-block px-3 py-1 bg-primary-100 text-primary-800 text-sm font-semibold rounded-full">
                      Division {results.csi_code.division}
                    </span>
                    <h3 className="text-xl font-bold text-neutral-900">{results.csi_code.code}</h3>
                  </div>
                  <h4 className="text-lg font-semibold text-neutral-800 mb-2">{results.csi_code.title}</h4>
                  <p className="text-neutral-600">{results.csi_code.description}</p>
                </div>
                <div className="bg-accent-100 text-accent-800 px-3 py-1 rounded-lg text-sm font-medium">
                  {results.total_results} {results.total_results === 1 ? 'Section' : 'Sections'}
                </div>
              </div>
            </div>

            {/* ICC Sections */}
            <div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Related ICC Code Sections</h3>
              <div className="space-y-4">
                {results.icc_sections.map((section) => (
                  <div key={section.id} className="bg-white rounded-xl shadow-md border border-neutral-200 p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="inline-block px-2 py-1 bg-neutral-100 text-neutral-700 text-xs font-medium rounded">
                            {section.document.code} {section.document.year}
                          </span>
                          {section.document.state && (
                            <span className="inline-block px-2 py-1 bg-accent-100 text-accent-800 text-xs font-medium rounded">
                              {section.document.state}
                            </span>
                          )}
                          <span className="text-sm text-neutral-500">Chapter {section.chapter}</span>
                        </div>
                        <h4 className="text-lg font-semibold text-neutral-900 mb-1">
                          Section {section.section_number}: {section.title}
                        </h4>
                        <p className="text-neutral-600 text-sm mb-3">{section.description}</p>
                      </div>
                    </div>
                    <a
                      href={section.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium text-sm transition"
                    >
                      <span>View Full Section on ICC Website</span>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!results && !error && !loading && (
          <div className="bg-white rounded-xl shadow-md border border-neutral-200 p-12 text-center">
            <svg className="w-16 h-16 mx-auto text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">Start Your Search</h3>
            <p className="text-neutral-600 mb-4">Enter a CSI code above to find related ICC building code sections</p>
            <p className="text-sm text-neutral-500">Example: Try searching for <code className="px-2 py-1 bg-neutral-100 rounded">03 30 00</code></p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-neutral-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-neutral-600">
            CSI MasterFormat to ICC Code Mapping Tool • Data sourced from{' '}
            <a href="https://codes.iccsafe.org" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-700 font-medium">
              codes.iccsafe.org
            </a>
            and{' '}
            <a href="https://crmservice.csinet.org/widgets/masterformat/numbersandtitles.aspx" target="_blank" rel="noopener noreferrer" className="text-prinary-600 hover:text-primary-700 font-medium">
              crmservice.csinet.org
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
