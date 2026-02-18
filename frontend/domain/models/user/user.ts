export class UserItem {
  constructor(
    readonly id: number,
    readonly username: string,
    readonly isSuperuser: boolean,
    readonly isStaff: boolean,
    readonly email?: string,
    readonly firstName?: string,
    readonly lastName?: string,
    readonly groups?: number[],
    readonly dateJoined?: string,
    readonly lastLogin?: string
  ) {}
}

export interface UserUpdateData {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  groups: number[]
}

export interface UserPasswordData {
  password1: string
  password2: string
}

export interface UserDetailResponse {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
  groups: number[]
  date_joined: string
  last_log: string
}
