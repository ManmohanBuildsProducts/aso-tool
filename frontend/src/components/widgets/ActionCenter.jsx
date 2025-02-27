import React, { useState } from 'react';
import { HiLightningBolt, HiCheck, HiArrowRight } from 'react-icons/hi';
import { useMutation, useQueryClient } from 'react-query';
import { implementAction } from '../../services/api';
import toast from 'react-hot-toast';

const ActionCenter = ({ actions, appId }) => {
  const [filter, setFilter] = useState('all');
  const queryClient = useQueryClient();

  const implementMutation = useMutation(implementAction, {
    onSuccess: () => {
      queryClient.invalidateQueries(['appAnalysis', appId]);
      toast.success('Action implemented successfully');
    },
    onError: () => {
      toast.error('Failed to implement action');
    }
  });

  const filteredActions = actions?.filter(action => {
    if (filter === 'quick') return action.effort === 'low';
    if (filter === 'high') return action.impact >= 80;
    return true;
  });

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          Action Center
        </h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm"
        >
          <option value="all">All Actions</option>
          <option value="quick">Quick Wins</option>
          <option value="high">High Impact</option>
        </select>
      </div>

      <div className="space-y-4">
        {filteredActions?.map((action) => (
          <div
            key={action.id}
            className={`
              p-4 rounded-lg border-l-4
              ${action.priority === 'high' 
                ? 'border-red-500 bg-red-50'
                : action.priority === 'medium'
                  ? 'border-yellow-500 bg-yellow-50'
                  : 'border-blue-500 bg-blue-50'
              }
            `}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  {action.effort === 'low' && (
                    <HiLightningBolt className="w-5 h-5 text-yellow-500" />
                  )}
                  <h3 className="font-medium text-gray-900">
                    {action.title}
                  </h3>
                </div>
                <p className="mt-1 text-sm text-gray-600">
                  {action.description}
                </p>
              </div>

              <button
                onClick={() => implementMutation.mutate({
                  appId,
                  actionId: action.id
                })}
                disabled={implementMutation.isLoading}
                className={`
                  flex items-center gap-1 px-3 py-1 rounded-lg
                  ${action.status === 'done'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-white text-blue-600 hover:bg-blue-50'
                  }
                `}
              >
                {action.status === 'done' ? (
                  <>
                    <HiCheck className="w-4 h-4" />
                    <span>Done</span>
                  </>
                ) : (
                  <>
                    <span>Implement</span>
                    <HiArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            {action.steps && (
              <div className="mt-3 space-y-2">
                {action.steps.map((step, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 text-sm"
                  >
                    <div className={`
                      w-5 h-5 rounded-full flex items-center justify-center
                      ${step.status === 'done'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-400'
                      }
                    `}>
                      {step.status === 'done' ? (
                        <HiCheck className="w-3 h-3" />
                      ) : (
                        <span>{index + 1}</span>
                      )}
                    </div>
                    <span className={
                      step.status === 'done'
                        ? 'text-gray-400 line-through'
                        : 'text-gray-600'
                    }>
                      {step.action}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ActionCenter;