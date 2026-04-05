import { UserItem, UserUpdateData, UserPasswordData, UserDetailResponse } from '@/domain/models/user/user'
import { APIUserRepository } from '@/repositories/user/apiUserRepository'

export class UserApplicationService {
  private repository: APIUserRepository

  constructor(repository: APIUserRepository) {
    this.repository = repository
  }

  public async getProfile(): Promise<UserItem> {
    return await this.repository.getProfile()
  }

  public async list(query: string = ''): Promise<UserItem[]> {
    return await this.repository.list(query)
  }

  public async getById(userId: number): Promise<UserDetailResponse> {
    return await this.repository.getById(userId)
  }

  public async update(userData: UserUpdateData): Promise<void> {
    return await this.repository.update(userData)
  }

  public async setPassword(userId: number, passwordData: UserPasswordData): Promise<void> {
    return await this.repository.setPassword(userId, passwordData)
  }

  public async updateWithPassword(userData: UserUpdateData, newPassword?: string, confirmPassword?: string): Promise<void> {
    // Validate passwords if provided
    if (newPassword || confirmPassword) {
      if (newPassword !== confirmPassword) {
        throw new Error('The passwords do not match!')
      }
      if (!newPassword || !confirmPassword) {
        throw new Error('Both password fields must be filled!')
      }
      
      try {
        // Set password first - now we know both are strings
        await this.setPassword(userData.id, {
          password1: newPassword,
          password2: confirmPassword
        })
      } catch (error: any) {
        // Re-throw password validation errors with clearer messages
        if (error.response?.data?.error) {
          throw new Error(error.response.data.error)
        }
        throw error
      }
    }
    
    // Update user data
    await this.update(userData)
  }
} 