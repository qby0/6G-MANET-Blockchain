#include "ns3_simple_blockchain.h"
#include "ns3/log.h"
#include "ns3/string.h"
#include "ns3/double.h"
#include "ns3/uinteger.h"
#include "ns3/simulator.h"
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <sys/stat.h>

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("SimpleBlockchain");

//
// SimpleBlockchain
//
NS_OBJECT_ENSURE_REGISTERED (SimpleBlockchain);

TypeId
SimpleBlockchain::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::SimpleBlockchain")
    .SetParent<Object> ()
    .SetGroupName ("Applications")
    .AddConstructor<SimpleBlockchain> ()
    ;
  return tid;
}

SimpleBlockchain::SimpleBlockchain ()
  : m_transactionCounter (0),
    m_lastResultCheck (0.0)
{
  NS_LOG_FUNCTION (this);
}

SimpleBlockchain::~SimpleBlockchain ()
{
  NS_LOG_FUNCTION (this);
}

void
SimpleBlockchain::Initialize (const std::string& ipcDir)
{
  NS_LOG_FUNCTION (this << ipcDir);
  
  m_ipcDir = ipcDir;
  m_ns3ToBlocksimFile = m_ipcDir + "/ns3_to_blocksim.json";
  m_blocksimToNs3File = m_ipcDir + "/blocksim_to_ns3.json";
  m_statusFile = m_ipcDir + "/bridge_status.json";
  
  // Create IPC directory if it doesn't exist
  mkdir(m_ipcDir.c_str(), 0755);
  
  NS_LOG_INFO ("SimpleBlockchain initialized with IPC dir: " << m_ipcDir);
  
  // Initialize with empty transaction file
  WriteFile(m_ns3ToBlocksimFile, "{\"transactions\": [], \"timestamp\": " + 
            std::to_string(Simulator::Now().GetSeconds()) + "}");
}

std::string
SimpleBlockchain::SendTransaction (uint32_t senderId, uint32_t recipientId, 
                                  const std::string& data, 
                                  const std::string& txId)
{
  NS_LOG_FUNCTION (this << senderId << recipientId << data);
  
  std::string transactionId = txId.empty() ? GenerateTransactionId() : txId;
  
  // Store as pending transaction
  std::ostringstream txData;
  txData << "{";
  txData << "\"tx_id\": \"" << transactionId << "\", ";
  txData << "\"sender_id\": " << senderId << ", ";
  txData << "\"recipient_id\": " << recipientId << ", ";
  txData << "\"data\": \"" << data << "\", ";
  txData << "\"timestamp\": " << Simulator::Now().GetSeconds();
  txData << "}";
  
  m_pendingTransactions[transactionId] = txData.str();
  
  NS_LOG_INFO ("Created transaction " << transactionId << 
               " from node " << senderId << " to " << recipientId);
  
  // Write all pending transactions to file
  WriteTransactionsToFile();
  
  return transactionId;
}

bool
SimpleBlockchain::IsTransactionValidated (const std::string& txId)
{
  return m_validatedTransactions.find(txId) != m_validatedTransactions.end();
}

std::string
SimpleBlockchain::GetTransactionResult (const std::string& txId)
{
  auto it = m_validatedTransactions.find(txId);
  if (it != m_validatedTransactions.end())
    {
      return it->second;
    }
  return "";
}

int
SimpleBlockchain::ProcessBlockSimResults ()
{
  NS_LOG_FUNCTION (this);
  
  double currentTime = Simulator::Now().GetSeconds();
  
  // Don't check too frequently
  if (currentTime - m_lastResultCheck < 0.1)
    {
      return 0;
    }
  
  m_lastResultCheck = currentTime;
  
  // Read results from BlockSim
  std::string content = ReadFile(m_blocksimToNs3File);
  if (content.empty())
    {
      return 0;
    }
  
  // Simple parsing: look for "tx_id" and "validated": true
  // In real implementation, use proper JSON parser
  int newResults = 0;
  std::string::size_type pos = 0;
  
  while ((pos = content.find("\"tx_id\":", pos)) != std::string::npos)
    {
      // Extract transaction ID
      pos += 9; // Skip "tx_id":
      std::string::size_type start = content.find("\"", pos) + 1;
      std::string::size_type end = content.find("\"", start);
      
      if (start != std::string::npos && end != std::string::npos)
        {
          std::string txId = content.substr(start, end - start);
          
          // Check if already processed
          if (m_validatedTransactions.find(txId) == m_validatedTransactions.end())
            {
              // Look for validation status
              std::string::size_type validatedPos = content.find("\"validated\":", end);
              if (validatedPos != std::string::npos)
                {
                  validatedPos += 12; // Skip "validated":
                  bool validated = content.substr(validatedPos, 4) == "true";
                  
                  if (validated)
                    {
                      // Extract the full result (simplified)
                      std::string::size_type resultStart = content.rfind("{", pos);
                      std::string::size_type resultEnd = content.find("}", end) + 1;
                      
                      if (resultStart != std::string::npos && resultEnd != std::string::npos)
                        {
                          std::string result = content.substr(resultStart, resultEnd - resultStart);
                          m_validatedTransactions[txId] = result;
                          
                          // Remove from pending
                          m_pendingTransactions.erase(txId);
                          
                          newResults++;
                          
                          NS_LOG_INFO ("Transaction " << txId << " validated by BlockSim");
                        }
                    }
                }
            }
        }
      
      pos = end;
    }
  
  return newResults;
}

bool
SimpleBlockchain::IsBridgeActive ()
{
  std::string content = ReadFile(m_statusFile);
  return content.find("\"bridge_active\": true") != std::string::npos;
}

std::string
SimpleBlockchain::GenerateTransactionId ()
{
  std::ostringstream oss;
  oss << "ns3_tx_" << Simulator::Now().GetSeconds() << "_" << (++m_transactionCounter);
  return oss.str();
}

void
SimpleBlockchain::WriteTransactionsToFile ()
{
  if (m_pendingTransactions.empty())
    {
      return;
    }
  
  std::ostringstream json;
  json << "{\"transactions\": [";
  
  bool first = true;
  for (const auto& tx : m_pendingTransactions)
    {
      if (!first) json << ", ";
      json << tx.second;
      first = false;
    }
  
  json << "], \"timestamp\": " << Simulator::Now().GetSeconds() << "}";
  
  WriteFile(m_ns3ToBlocksimFile, json.str());
  
  NS_LOG_DEBUG ("Wrote " << m_pendingTransactions.size() << " transactions to file");
}

std::string
SimpleBlockchain::ReadFile (const std::string& filename)
{
  std::ifstream file(filename);
  if (!file.is_open())
    {
      return "";
    }
  
  std::string content((std::istreambuf_iterator<char>(file)),
                      std::istreambuf_iterator<char>());
  file.close();
  
  return content;
}

void
SimpleBlockchain::WriteFile (const std::string& filename, const std::string& content)
{
  std::ofstream file(filename);
  if (file.is_open())
    {
      file << content;
      file.close();
    }
}

//
// SimpleBlockchainApp
//
NS_OBJECT_ENSURE_REGISTERED (SimpleBlockchainApp);

TypeId
SimpleBlockchainApp::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::SimpleBlockchainApp")
    .SetParent<Application> ()
    .SetGroupName ("Applications")
    .AddConstructor<SimpleBlockchainApp> ()
    .AddAttribute ("CheckInterval",
                   "Interval to check blockchain results",
                   TimeValue (Seconds (1.0)),
                   MakeTimeAccessor (&SimpleBlockchainApp::m_checkInterval),
                   MakeTimeChecker ())
    ;
  return tid;
}

SimpleBlockchainApp::SimpleBlockchainApp ()
  : m_checkInterval (Seconds (1.0)),
    m_testCounter (0)
{
  NS_LOG_FUNCTION (this);
}

SimpleBlockchainApp::~SimpleBlockchainApp ()
{
  NS_LOG_FUNCTION (this);
}

void
SimpleBlockchainApp::SetBlockchain (Ptr<SimpleBlockchain> blockchain)
{
  m_blockchain = blockchain;
}

void
SimpleBlockchainApp::SendTestTransaction (uint32_t recipientId, const std::string& data)
{
  if (m_blockchain)
    {
      uint32_t nodeId = GetNode()->GetId();
      std::string txId = m_blockchain->SendTransaction(nodeId, recipientId, data);
      NS_LOG_INFO ("Node " << nodeId << " sent test transaction " << txId);
    }
}

void
SimpleBlockchainApp::StartApplication (void)
{
  NS_LOG_FUNCTION (this);
  
  // Schedule periodic blockchain result checking
  m_checkEvent = Simulator::Schedule (m_checkInterval, 
                                     &SimpleBlockchainApp::CheckBlockchainResults, this);
}

void
SimpleBlockchainApp::StopApplication (void)
{
  NS_LOG_FUNCTION (this);
  
  if (m_checkEvent.IsRunning())
    {
      Simulator::Cancel (m_checkEvent);
    }
}

void
SimpleBlockchainApp::CheckBlockchainResults ()
{
  if (m_blockchain)
    {
      int newResults = m_blockchain->ProcessBlockSimResults();
      if (newResults > 0)
        {
          NS_LOG_INFO ("Node " << GetNode()->GetId() << 
                       " processed " << newResults << " blockchain results");
        }
    }
  
  // Schedule next check
  m_checkEvent = Simulator::Schedule (m_checkInterval, 
                                     &SimpleBlockchainApp::CheckBlockchainResults, this);
}

} // namespace ns3 