// APIService.swift
// 网络请求服务
//
// 对应小程序: wx.request() 的封装

import Foundation

class APIService {
    static let shared = APIService()

    private init() {}

    // MARK: - Generic Request Method

    func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        parameters: [String: Any]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        guard let url = URL(string: endpoint) else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30

        if let parameters = parameters {
            do {
                request.httpBody = try JSONSerialization.data(withJSONObject: parameters)
            } catch {
                completion(.failure(error))
                return
            }
        }

        print("📡 [API] \(method) \(endpoint)")
        if let params = parameters {
            print("📤 [API] 参数: \(params)")
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("❌ [API] 错误: \(error.localizedDescription)")
                completion(.failure(error))
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(NSError(domain: "Invalid Response", code: -1)))
                return
            }

            print("📥 [API] 状态码: \(httpResponse.statusCode)")

            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }

            // 打印响应数据(调试用)
            if let jsonString = String(data: data, encoding: .utf8) {
                print("📥 [API] 响应: \(jsonString.prefix(200))...")
            }

            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let result = try decoder.decode(T.self, from: data)
                print("✅ [API] 解析成功")
                completion(.success(result))
            } catch {
                print("❌ [API] 解析失败: \(error)")
                completion(.failure(error))
            }
        }.resume()
    }

    // MARK: - API Endpoints

    /// 获取岗位列表
    func fetchPositions(completion: @escaping (Result<[PositionCategory], Error>) -> Void) {
        request(Constants.API.positions) { (result: Result<PositionsResponse, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.categories))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    /// 搜索岗位
    func searchPositions(keyword: String, completion: @escaping (Result<[Position], Error>) -> Void) {
        let endpoint = "\(Constants.API.positionsSearch)?keyword=\(keyword.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
        request(endpoint, completion: completion)
    }

    /// 获取面试官风格列表
    func fetchInterviewerStyles(round: String?, completion: @escaping (Result<[InterviewerStyle], Error>) -> Void) {
        var endpoint = Constants.API.interviewerStyles
        if let round = round {
            endpoint += "?round=\(round.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
        }

        request(endpoint) { (result: Result<InterviewerStylesResponse, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.styles))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    /// 开始面试
    func startInterview(
        request startRequest: InterviewStartRequest,
        completion: @escaping (Result<InterviewStartResponse, Error>) -> Void
    ) {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase

        guard let data = try? encoder.encode(startRequest),
              let dict = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            completion(.failure(NSError(domain: "Encoding Error", code: -1)))
            return
        }

        self.request(Constants.API.startInterview, method: "POST", parameters: dict, completion: completion)
    }

    /// 提交回答
    func submitAnswer(
        request answerRequest: AnswerRequest,
        completion: @escaping (Result<AnswerResponse, Error>) -> Void
    ) {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase

        guard let data = try? encoder.encode(answerRequest),
              let dict = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            completion(.failure(NSError(domain: "Encoding Error", code: -1)))
            return
        }

        self.request(Constants.API.answer, method: "POST", parameters: dict, completion: completion)
    }

    /// 获取面试报告
    func fetchReport(sessionId: String, completion: @escaping (Result<InterviewReport, Error>) -> Void) {
        let endpoint = "\(Constants.API.report)/\(sessionId)"
        request(endpoint, completion: completion)
    }

    /// 获取面试历史
    func fetchHistory(userId: String, completion: @escaping (Result<[InterviewHistoryItem], Error>) -> Void) {
        let endpoint = "\(Constants.API.interviewHistory)?user_id=\(userId)"
        request(endpoint, completion: completion)
    }

    /// 获取用户信息
    func fetchUserProfile(userId: String, completion: @escaping (Result<UserInfo, Error>) -> Void) {
        let endpoint = "\(Constants.API.userProfile)?user_id=\(userId)"
        request(endpoint, completion: completion)
    }
}
