import React, { useState } from 'react';
import { HiSearch, HiTrendingUp, HiTrendingDown, HiStar } from 'react-icons/hi';

const KeywordTable = ({ data }) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const variations = data?.analysis?.variations || [];
  const longTail = data?.analysis?.long_tail || [];
  const relatedTerms = data?.analysis?.related_terms || [];

  // Combine all keywords
  const allKeywords = [
    ...variations.map(v => ({
      ...v,
      type: 'variation'
    })),
    ...longTail.map(lt => ({
      keyword: lt.keyword,
      relevance: 1,
      competition: lt.opportunity === 'high' ? 'low' : 'medium',
      priority: lt.opportunity,
      type: 'long_tail',
      search_intent: lt.search_intent
    })),
    ...relatedTerms.map(rt => ({
      keyword: rt.term,
      relevance: rt.relevance,
      competition: 'medium',
      priority: rt.relevance > 0.7 ? 'high' : 'medium',
      type: 'related',
      category: rt.category
    }))
  ];

  // Filter keywords
  const filteredKeywords = allKeywords.filter(kw => {
    const matchesSearch = kw.keyword.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || 
                         (filter === 'high' && kw.priority === 'high') ||
                         (filter === 'long_tail' && kw.type === 'long_tail');
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="bg-white rounded-xl shadow-lg p-6" data-testid="keyword-table">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          Keyword Analysis
        </h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border rounded-lg text-sm"
            />
            <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 border rounded-lg text-sm"
          >
            <option value="all">All Keywords</option>
            <option value="high">High Priority</option>
            <option value="long_tail">Long Tail</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Keyword</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Type</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Priority</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Competition</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredKeywords.map((kw, index) => (
              <tr 
                key={index}
                className="border-b border-gray-100 hover:bg-gray-50"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center">
                    {kw.priority === 'high' && (
                      <HiStar className="w-4 h-4 text-yellow-400 mr-2" />
                    )}
                    <span className="text-sm text-gray-900">{kw.keyword}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`
                    text-xs px-2 py-1 rounded-full
                    ${kw.type === 'variation' ? 'bg-blue-100 text-blue-700' :
                      kw.type === 'long_tail' ? 'bg-purple-100 text-purple-700' :
                      'bg-green-100 text-green-700'}
                  `}>
                    {kw.type}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`
                    text-xs px-2 py-1 rounded-full
                    ${kw.priority === 'high' ? 'bg-red-100 text-red-700' :
                      kw.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'}
                  `}>
                    {kw.priority}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center">
                    {kw.competition === 'high' ? (
                      <HiTrendingUp className="w-4 h-4 text-red-500 mr-1" />
                    ) : kw.competition === 'medium' ? (
                      <HiTrendingDown className="w-4 h-4 text-yellow-500 mr-1" />
                    ) : (
                      <HiTrendingDown className="w-4 h-4 text-green-500 mr-1" />
                    )}
                    <span className="text-sm text-gray-600">
                      {kw.competition}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-gray-600">
                    {kw.search_intent || kw.category || 
                     `Relevance: ${Math.round(kw.relevance * 100)}%`}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recommendations */}
      {data?.analysis?.recommendations && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <h3 className="font-medium text-green-900 mb-2">
            Optimization Tips
          </h3>
          <ul className="space-y-2 text-sm text-green-700">
            {data.analysis.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-2">
                <span>•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default KeywordTable;