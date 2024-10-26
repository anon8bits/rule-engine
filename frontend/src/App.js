import React, { useState, useEffect } from 'react';
import { PlusCircle, CheckCircle, Combine } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Alert, AlertDescription } from './components/ui/alert';

const App = () => {
  const [rules, setRules] = useState([]);
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleString, setNewRuleString] = useState('');
  const [jsonData, setJsonData] = useState('');
  const [selectedRule, setSelectedRule] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedRules, setSelectedRules] = useState([]);
  const [combinedRuleName, setCombinedRuleName] = useState('');

  // Fetch rules on component mount
  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/rules');
      const data = await response.json();
      setRules(data);
    } catch (err) {
      setError('Failed to fetch rules');
    }
  };

  const addRule = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/rules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newRuleName,
          rule_string: newRuleString,
        }),
      });
      
      if (!response.ok) throw new Error('Failed to add rule');
      
      await fetchRules();
      setNewRuleName('');
      setNewRuleString('');
    } catch (err) {
      setError('Failed to add rule');
    }
  };

  const evaluateData = async () => {
    if (!selectedRule || !jsonData) return;
    
    try {
      const parsedData = JSON.parse(jsonData);
      const response = await fetch(`http://localhost:8000/api/rules/${selectedRule}/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedData),
      });
      
      const res = await response.json();
      setEvaluationResult(res.result);
    } catch (err) {
      setError('Failed to evaluate data');
    }
  };

  const combineRules = async () => {
    if (selectedRules.length !== 2) return;
    
    try {
      const response = await fetch('http://localhost:8000/api/rules/combine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rule_ids: selectedRules,
          save_rule: true,
          name: combinedRuleName,
        }),
      });
      
      if (!response.ok) throw new Error('Failed to combine rules');
      
      await fetchRules();
      setSelectedRules([]);
      setCombinedRuleName('');
    } catch (err) {
      setError('Failed to combine rules');
    }
  };

  const toggleRuleSelection = (ruleId) => {
    if (selectedRules.includes(ruleId)) {
      setSelectedRules(selectedRules.filter(id => id !== ruleId));
    } else if (selectedRules.length < 2) {
      setSelectedRules([...selectedRules, ruleId]);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Add New Rule</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Rule Name"
            value={newRuleName}
            onChange={(e) => setNewRuleName(e.target.value)}
          />
          <Input
            placeholder="Rule String. Make sure to use single quotes for strings and parentheses for grouping."
            value={newRuleString}
            onChange={(e) => setNewRuleString(e.target.value)}
          />
          <Button onClick={addRule} className="w-full">
            <PlusCircle className="mr-2 h-4 w-4" />
            Add Rule
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Evaluate Data</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder='JSON Data (e.g., {"age": 35, "department": "Sales"})'
            value={jsonData}
            onChange={(e) => setJsonData(e.target.value)}
          />
          <select 
            className="w-full p-2 border rounded-md"
            onChange={(e) => setSelectedRule(e.target.value)}
            value={selectedRule || ''}
          >
            <option value="">Select a rule to evaluate</option>
            {rules.map(rule => (
              <option key={rule.id} value={rule.id}>
                {rule.name}: {rule.rule_string}
              </option>
            ))}
          </select>
          <Button onClick={evaluateData} className="w-full">
            <CheckCircle className="mr-2 h-4 w-4" />
            Evaluate
          </Button>
          {evaluationResult !== null && (
            <div className="mt-4 p-4 bg-gray-100 rounded-md">
              Result: {evaluationResult ? 'True' : 'False'}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Combine Rules</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Combined Rule Name"
            value={combinedRuleName}
            onChange={(e) => setCombinedRuleName(e.target.value)}
          />
          <Button onClick={combineRules} className="w-full" disabled={selectedRules.length !== 2}>
            <Combine className="mr-2 h-4 w-4" />
            Combine Selected Rules
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Rules List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {rules.map(rule => (
              <div 
                key={rule.id} 
                className={`p-4 border rounded-md cursor-pointer ${
                  selectedRules.includes(rule.id) ? 'bg-blue-100' : ''
                }`}
                onClick={() => toggleRuleSelection(rule.id)}
              >
                <div className="font-medium">ID: {rule.id}</div>
                <div>Name: {rule.name}</div>
                <div className="text-sm text-gray-600">Rule: {rule.rule_string}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default App;