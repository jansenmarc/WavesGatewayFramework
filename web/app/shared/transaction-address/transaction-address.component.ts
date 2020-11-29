import {
  AfterViewInit,
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges
} from '@angular/core';
import { PublicConfigurationService } from '../public.configuration.service';
import { PublicConfiguration } from '../public-configuration.model';

@Component({
  selector: 'app-transaction-address',
  templateUrl: './transaction-address.component.html',
  styleUrls: ['./transaction-address.component.scss']
})
export class TransactionAddressComponent
  implements OnInit, OnChanges, AfterViewInit {
  publicConfiguration: PublicConfiguration;
  href: string;
  @Input() address: string;
  @Input() currency: string;

  replacedAddress: string;

  constructor(publicConfigurationService: PublicConfigurationService) {
    this.publicConfiguration = publicConfigurationService.configuration;
  }

  ngOnInit() {
    this.reset();
  }

  private reset() {
    this.resetAddress();
    this.resetHref();
  }

  ngAfterViewInit(): void {
    this.reset();
  }

  private resetHref() {
    if (this.address && this.currency && this.publicConfiguration) {
      if (
        this.currency === 'coin' &&
        this.publicConfiguration.coin_address_web_link
      ) {
        this.href = this.publicConfiguration.coin_address_web_link.replace(
          '{{address}}',
          this.address
        );
      } else if (
        this.currency === 'waves' &&
        this.publicConfiguration.waves_address_web_link
      ) {
        this.href = this.publicConfiguration.waves_address_web_link.replace(
          '{{address}}',
          this.address
        );
      } else {
        this.href = null;
      }
    } else {
      this.href = null;
    }
  }

  private resetAddress() {
    if (
      this.currency === 'coin' &&
      this.address === this.publicConfiguration.gateway_coin_holder
    ) {
      this.replacedAddress = `Gateway ${this.publicConfiguration
        .custom_currency_name} Address`;
    } else if (
      this.currency === 'waves' &&
      this.address === this.publicConfiguration.gateway_waves_address
    ) {
      this.replacedAddress = 'Gateway ${this.publicConfiguration
        .base_currency_name} Address';
    } else {
      this.replacedAddress = this.address;
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.reset();
  }
}
