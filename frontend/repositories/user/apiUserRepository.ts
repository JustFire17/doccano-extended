import { UserItem, UserUpdateData, UserPasswordData, UserDetailResponse } from '@/domain/models/user/user'
import ApiService from '@/services/api.service'

function toModel(item: { [key: string]: any }): UserItem {
  return new UserItem(
    item.id, 
    item.username, 
    item.is_superuser, 
    item.is_staff,
    item.email,
    item.first_name,
    item.last_name,
    item.groups,
    item.date_joined,
    item.last_log
  )
}

export class APIUserRepository {
  constructor(private readonly request = ApiService) {}

  async getProfile(): Promise<UserItem> {
    const url = '/me'
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  async list(query: string): Promise<UserItem[]> {
    const url = `/users?q=${query}`
    const response = await this.request.get(url)
    return response.data.map((item: { [key: string]: any }) => toModel(item))
  }

  async getById(userId: number): Promise<UserDetailResponse> {
    const url = `/users/${userId}`
    const response = await this.request.get(url)
    return response.data
  }

  async update(userData: UserUpdateData): Promise<void> {
    const url = `/users/update/${userData.id}`
    await this.request.patch(url, userData)
  }

  async setPassword(userId: number, passwordData: UserPasswordData): Promise<void> {
    const url = `/users/${userId}/set_password/`
    await this.request.post(url, passwordData)
  }
}
